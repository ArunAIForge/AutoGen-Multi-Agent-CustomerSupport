import asyncio
import time
from typing import Dict, Any, List, Optional
from config.settings import get_model_client
from utils.logger import app_logger
from utils.validation import validate_support_query
from agents.main_agent import (
    create_main_agent,
    create_response_validator_agent,
    route_user_query,
    validate_and_finalize_response
)
from agents.hr_agent import create_hr_agent
from agents.it_agent import create_it_agent
from agents.insurance_agent import create_insurance_agent
from agents.admin_agent import create_admin_agent
from agents.accounts_agent import create_accounts_agent

AGENT_REGISTRY = {
    "HR": create_hr_agent,
    "IT": create_it_agent,
    "INSURANCE": create_insurance_agent,
    "ADMIN": create_admin_agent,
    "ACCOUNTS": create_accounts_agent
}

async def process_support_query(
    query: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    start_time = time.time()
    app_logger.info(f"Incoming Support Query: \"{query}\"")
    
    # 1. Input Validation
    is_valid, validation_error = validate_support_query(query)
    if not is_valid:
        app_logger.warning(f"Validation Failed: {validation_error}")
        return {
            "status": "INVALID",
            "department": "Input Validation",
            "response": validation_error,
            "reasoning": "Pre-execution input validation failed.",
            "latency": round(time.time() - start_time, 2),
            "confidence": 0.0
        }
        
    try:
        # 2. Model Client & Coordinators
        model_client = get_model_client(model=model, temperature=temperature, api_key=api_key)
        coordinator = create_main_agent(model_client)
        validator = create_response_validator_agent(model_client)
        
        # 3. Intent Routing
        routing_decision = await route_user_query(coordinator, query)
        status = routing_decision.get("status", "AMBIGUOUS").upper()
        department = routing_decision.get("department", "NONE").upper()
        reasoning = routing_decision.get("reasoning", "")
        fallback_msg = routing_decision.get("clarification_or_fallback", "")
        confidence = routing_decision.get("confidence", 0.0)
        
        app_logger.info(f"Routing Decision: Status={status} | Dept={department} | Conf={confidence}")
        
        # 4. Handle Ambiguity & Out-of-Scope (Short-circuit)
        if status in ["AMBIGUOUS", "OUT_OF_SCOPE"] or department not in AGENT_REGISTRY:
            if not fallback_msg:
                fallback_msg = (
                    "Could you please clarify your request? Please specify whether "
                    "your inquiry is for HR, IT, Insurance, Admin, or Accounts."
                )
            latency = round(time.time() - start_time, 2)
            return {
                "status": status,
                "department": "Main Coordinator" if department == "NONE" else department,
                "response": fallback_msg,
                "reasoning": reasoning,
                "latency": latency,
                "confidence": confidence
            }
            
        # 5. Execute Targeted Specialized Agent
        agent_factory = AGENT_REGISTRY[department]
        specialized_agent = agent_factory(model_client)
        
        prompt_with_context = query
        if conversation_history:
            context_summary = "\n".join([
                f"{m.get('role', 'user').title()}: {m.get('content', '')}"
                for m in conversation_history[-3:]
            ])
            prompt_with_context = (
                f"Context from recent conversation:\n{context_summary}\n\n"
                f"Current User Query: {query}"
            )
            
        app_logger.info(f"Executing Specialist [{department}_Agent]...")
        agent_run = await specialized_agent.run(task=prompt_with_context)
        raw_response = agent_run.messages[-1].content
        
        # 6. Response Validation
        app_logger.info(f"Validating [{department}_Agent] response...")
        validated_response = await validate_and_finalize_response(
            validator=validator,
            query=query,
            department=department,
            agent_response=raw_response
        )
        
        latency = round(time.time() - start_time, 2)
        app_logger.info(f"Completed in {latency}s by {department}_Agent.")
        
        return {
            "status": "SUCCESS",
            "department": department,
            "response": validated_response,
            "reasoning": reasoning,
            "latency": latency,
            "confidence": confidence
        }
        
    except Exception as e:
        latency = round(time.time() - start_time, 2)
        app_logger.error(f"Execution Error: {str(e)}", exc_info=True)
        return {
            "status": "ERROR",
            "department": "System Fallback",
            "response": f"An unexpected error occurred: {str(e)}. Please check your API key and connection.",
            "reasoning": f"Exception raised: {str(e)}",
            "latency": latency,
            "confidence": 0.0
        }