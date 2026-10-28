import json
import logging
from typing import Dict, Any
from autogen_agentchat.agents import AssistantAgent

logger = logging.getLogger(__name__)

COORDINATOR_SYSTEM_MESSAGE = """You are the Central Coordinator and Triage Agent for an Enterprise Multi-Agent Customer Support System.

Your primary duties are:
1. VALIDATE: Ensure the user's query is coherent, safe, and related to enterprise workplace support.
2. CLASSIFY INTENT: Determine which specialized department should handle the query:
   - "HR": Leave policies, annual/sick leave, holidays, employee onboarding, attendance, HR procedures, code of conduct.
   - "IT": Passwords, VPN, network issues, software installation, system access, hardware troubleshooting, technical errors.
   - "INSURANCE": Health insurance policies, cashless hospitalization, coverage terms, claims submission, eligibility, insurance cards.
   - "ADMIN": Office facilities, ID cards, visitor badges, desk allocation, stationery, physical access, office maintenance.
   - "ACCOUNTS": Expense reimbursements, travel claims, payroll accounting, invoice queries, payment status, tax deductions.
   - "AMBIGUOUS": If the query is vague or missing essential context (e.g., "I need help with my status" or "Submit my claim"), do NOT route blindly. Ask the user a targeted, polite clarifying question.
   - "OUT_OF_SCOPE": If the query is completely unrelated to enterprise support (e.g., general trivia, personal chat, cooking recipes), politely decline and state the 5 supported departments.

3. OUTPUT FORMAT: When asked to route a query, you MUST return a valid JSON object strictly matching this schema:
{
    "status": "ROUTE" | "AMBIGUOUS" | "OUT_OF_SCOPE",
    "department": "HR" | "IT" | "INSURANCE" | "ADMIN" | "ACCOUNTS" | "NONE",
    "confidence": 0.0 to 1.0,
    "reasoning": "Short explanation of intent classification",
    "clarification_or_fallback": "Direct message to user if AMBIGUOUS or OUT_OF_SCOPE, otherwise empty string"
}

Respond ONLY with the JSON object, with no markdown formatting or markdown code blocks.
"""

RESPONSE_VALIDATOR_SYSTEM_MESSAGE = """You are the Quality Assurance and Response Validator for the Customer Support Coordinator.
Your duty is to review the specialized department agent's drafted response to a user query:
1. Ensure the response directly answers the user's question accurately and professionally.
2. Check that the tone is helpful, polite, and actionable.
3. If the response is good, return it directly.
4. If the response misses key user context, refine and polish it to be clear and complete for the end user.
"""

def create_main_agent(model_client) -> AssistantAgent:
    """Creates the Main Coordinator AssistantAgent."""
    return AssistantAgent(
        name="Main_Coordinator_Agent",
        model_client=model_client,
        system_message=COORDINATOR_SYSTEM_MESSAGE,
        description="Coordinates customer support queries, determines intent, and validates responses."
    )

def create_response_validator_agent(model_client) -> AssistantAgent:
    """Creates an agent specifically tasked with verifying and polishing final responses."""
    return AssistantAgent(
        name="Response_Validator_Agent",
        model_client=model_client,
        system_message=RESPONSE_VALIDATOR_SYSTEM_MESSAGE,
        description="Reviews and validates specialized department responses before delivery."
    )

async def route_user_query(coordinator: AssistantAgent, query: str) -> Dict[str, Any]:
    """
    Runs the coordinator agent on the user query to determine the routing decision.
    Returns a parsed dictionary containing status, department, and any message.
    """
    prompt = f"Analyze the following user query and provide your routing decision JSON:\n\nUser Query: \"{query}\""
    
    try:
        response = await coordinator.run(task=prompt)
        last_message = response.messages[-1].content
        
        # Clean markdown wrappers if returned
        cleaned = last_message.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        parsed = json.loads(cleaned)
        return parsed
    except Exception as e:
        logger.error(f"Error during query routing: {e}")
        return {
            "status": "AMBIGUOUS",
            "department": "NONE",
            "confidence": 0.0,
            "reasoning": f"Routing analysis error: {str(e)}",
            "clarification_or_fallback": "I had trouble analyzing your request. Could you please specify whether your query relates to HR, IT, Insurance, Admin, or Accounts?"
        }

async def validate_and_finalize_response(
    validator: AssistantAgent,
    query: str,
    department: str,
    agent_response: str
) -> str:
    """Reviews and polishes the specialized agent's response against the user query."""
    prompt = f"""User Query: "{query}"
Department: {department}
Specialized Agent Response:
\"\"\"{agent_response}\"\"\"

Please review and return the final, polished response for the user:"""
    
    try:
        validation_run = await validator.run(task=prompt)
        return validation_run.messages[-1].content.strip()
    except Exception as e:
        logger.warning(f"Response validation fallback: {e}")
        return agent_response