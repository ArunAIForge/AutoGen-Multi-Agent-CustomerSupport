import os
from dotenv import load_dotenv
from typing import Optional, Tuple, Dict, Any
from autogen_ext.models.openai import OpenAIChatCompletionClient
from utils.logger import app_logger

load_dotenv()

# Exactly 1 Free Model (Groq) and 1 Paid Model (OpenAI)
MODEL_PROFILES = {
    "openai/gpt-oss-20b": {
        "display_name": "openai/gpt-oss-20b (Groq - Free Cloud API)",
        "provider": "Groq",
        "default_base_url": "https://api.groq.com/openai/v1",
        "is_free": True,
        "env_key_var": "GROQ_API_KEY",
        "is_openai": False
    },
    "gpt-4o-mini": {
        "display_name": "gpt-4o-mini (OpenAI Key)",
        "provider": "OpenAI",
        "default_base_url": "https://api.openai.com/v1",
        "is_free": False,
        "env_key_var": "OPENAI_API_KEY",
        "is_openai": True
    }
}

def resolve_model_credentials(
    selected_model: str,
    user_api_key: Optional[str] = None
) -> Tuple[str, str, str, bool]:
    """Resolves model name, base URL, API key, and whether it is a native OpenAI model."""
    profile = MODEL_PROFILES.get(selected_model, {
        "display_name": selected_model,
        "provider": "Custom",
        "default_base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "is_free": False,
        "env_key_var": "OPENAI_API_KEY",
        "is_openai": False
    })
    
    base_url = os.getenv("OPENAI_BASE_URL", profile["default_base_url"])
    env_var = profile.get("env_key_var", "OPENAI_API_KEY")
    api_key = (
        user_api_key.strip() if user_api_key and user_api_key.strip()
        else os.getenv(env_var, "") or os.getenv("OPENAI_API_KEY", "")
    )
    
    is_openai = profile.get("is_openai", False)
    return selected_model, base_url, api_key, is_openai

def get_model_client(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    api_key: Optional[str] = None
) -> OpenAIChatCompletionClient:
    """Instantiates the model client for the selected provider with complete model_info."""
    default_model = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
    chosen_model = model or default_model
    default_temp = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    chosen_temp = temperature if temperature is not None else default_temp
    
    model_name, base_url, resolved_key, is_openai = resolve_model_credentials(chosen_model, api_key)
    app_logger.info(f"Instantiating Client | Model: {model_name} | Base URL: {base_url}")
    
    client_kwargs: Dict[str, Any] = {
        "model": model_name,
        "temperature": chosen_temp,
        "base_url": base_url,
    }
    
    if resolved_key:
        client_kwargs["api_key"] = resolved_key

    # ModelInfo for non-OpenAI endpoints (e.g. Groq)
    if not is_openai:
        client_kwargs["model_info"] = {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "unknown",
            "structured_output": True
        }
        
    return OpenAIChatCompletionClient(**client_kwargs)