import asyncio
import os
from dotenv import load_dotenv
from config.settings import get_model_client
from autogen_core.models import UserMessage

load_dotenv()

async def test_llm_connection():
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    print("=" * 60)
    print("Testing LLM Provider Connectivity...")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    print(f"API Key configured: {'YES (Key length: ' + str(len(api_key)) + ')' if api_key else 'NO (Missing)'}")
    print("=" * 60)
    
    if not api_key and not os.getenv("OPENAI_BASE_URL"):
        print("\n❌ Error: OPENAI_API_KEY is not set in your .env file.")
        print("Please edit your .env file and supply your API key before continuing.")
        return False
        
    try:
        client = get_model_client(model=model, temperature=0.1)
        response = await client.create(
            messages=[UserMessage(content="Respond with 'LLM connection successful!' and nothing else.", source="user")]
        )
        print(f"\n✅ Provider Response: {response.content}")
        print("\n🎉 Connection Verified! AutoGen can communicate with your LLM.")
        return True
    except Exception as e:
        print(f"\n❌ Connection Failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Verify your API key is active and has billing/quota available.")
        print("2. If using a corporate proxy or VPN, ensure api.openai.com is accessible.")
        print("3. If using Ollama/vLLM/Groq, ensure OPENAI_BASE_URL is set in .env.")
        return False

if __name__ == "__main__":
    asyncio.run(test_llm_connection())