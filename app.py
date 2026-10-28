import streamlit as st
import asyncio
import os
import json
from datetime import datetime
from services.orchestrator import process_support_query
from config.settings import MODEL_PROFILES

# ----------------- PAGE CONFIGURATION -----------------
st.set_page_config(
    page_title="Multi-Agent Customer Support",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- SESSION STATE INITIALIZATION -----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am your AI Support Coordinator. How can I assist you today? You can ask questions regarding HR, IT, Insurance, Office Admin, or Accounts & Reimbursements.",
            "department": "Main Agent",
            "timestamp": datetime.now().strftime("%H:%M")
        }
    ]

if "routing_history" not in st.session_state:
    st.session_state.routing_history = []

# ----------------- SIDEBAR CONTROLS & INFO -----------------
with st.sidebar:
    st.title("⚙️ System Control")
    st.caption("AutoGen Multi-Agent Architecture")

    st.markdown("### 🤖 LLM Model Selection")
    
    # Exactly 1 Free Model (Active on Groq) and 1 Paid Model (OpenAI)
    model_options = {
        "openai/gpt-oss-20b (Groq - Free Cloud API)": "openai/gpt-oss-20b",
        "gpt-4o-mini (OpenAI Key)": "gpt-4o-mini"
    }
    
    selected_label = st.selectbox(
        "Choose Model Provider",
        list(model_options.keys()),
        index=0,
        help="Select between the free Groq model and the paid OpenAI model"
    )
    selected_model = model_options[selected_label]
    profile = MODEL_PROFILES[selected_model]    

    # Dynamic status badge
    if profile["is_free"]:
        st.success(f"🟢 **Free Model:** {profile['provider']} Provider")
    else:
        st.info(f"🔑 **Paid Model:** {profile['provider']} (Requires API Key)")

    user_api_key = st.text_input(
        f"Custom API Key ({profile['provider']})",
        type="password",
        placeholder="Leave empty to use .env key",
        help=f"Optional: Override API key from .env for {profile['provider']}"
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        help="Lower values produce more deterministic responses"
    )

    st.divider()

    st.markdown("### 🏢 Supported Departments")
    st.markdown("""
    - 👥 **HR Agent**: Leave, holidays, onboarding, policies
    - 💻 **IT Agent**: Passwords, hardware, VPN, software access
    - 🛡️ **Insurance Agent**: Coverage, policy terms, claims
    - 🏢 **Admin Agent**: ID cards, office supplies, facilities
    - 💳 **Accounts Agent**: Reimbursements, payroll, invoices
    """)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Conversation cleared. How can I help you today?",
                    "department": "Main Agent",
                    "timestamp": datetime.now().strftime("%H:%M")
                }
            ]
            st.session_state.routing_history = []
            st.rerun()

    with col2:
        chat_json = json.dumps(st.session_state.messages, indent=2)
        st.download_button(
            "📥 Export",
            data=chat_json,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

    # Activity Log Viewer
    with st.expander("📜 View System Activity Log"):
        log_path = os.path.join("logs", "agent_activity.log")
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                logs = f.readlines()
                st.text("".join(logs[-15:]))
        else:
            st.caption("No log activity recorded yet.")

# ----------------- MAIN CHAT INTERFACE -----------------
st.title("🤖 Multi-Agent Customer Support Portal")
st.markdown("Submit any enterprise query. The **Coordinator Agent** validates the request, determines the intent, and delegates it to the specialized domain agent.")

# Render message history
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    dept = msg.get("department", "Support")
    time_str = msg.get("timestamp", "")
    reasoning = msg.get("reasoning", "")
    latency = msg.get("latency", None)
    
    with st.chat_message(role):
        if role == "assistant":
            meta = f"**Department:** `{dept}` | *{time_str}*"
            if latency is not None:
                meta += f" | ⚡ *{latency}s*"
            st.caption(meta)
        st.write(content)
        if reasoning:
            with st.expander("🔍 Routing & Intent Details"):
                st.caption(f"**Coordinator Reasoning:** {reasoning}")

# ----------------- CHAT INPUT HANDLING -----------------
if prompt := st.chat_input("Enter your support query (e.g., 'How do I claim medical insurance?' or 'Reset VPN password')..."):
    timestamp = datetime.now().strftime("%H:%M")
    
    # Append and display user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": timestamp
    })
    with st.chat_message("user"):
        st.write(prompt)
        
    # Execute AutoGen multi-agent orchestrator
    with st.chat_message("assistant"):
        with st.spinner(f"Coordinator Agent ({selected_model}) is analyzing intent and routing query..."):
            result = asyncio.run(process_support_query(
                query=prompt,
                conversation_history=st.session_state.messages,
                model=selected_model,
                temperature=temperature,
                api_key=user_api_key
            ))
            
            department = result.get("department", "Main Coordinator")
            answer = result.get("response", "No response generated.")
            reasoning = result.get("reasoning", "")
            latency = result.get("latency", 0.0)
            
            meta = f"**Department:** `{department}` | *{timestamp}* | ⚡ *{latency}s*"
            st.caption(meta)
            st.write(answer)
            if reasoning:
                with st.expander("🔍 Routing & Intent Details"):
                    st.caption(f"**Coordinator Reasoning:** {reasoning}")
            
            # Save assistant response to state
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "department": department,
                "reasoning": reasoning,
                "latency": latency,
                "timestamp": timestamp
            })
            
            st.session_state.routing_history.append({
                "query": prompt,
                "department": department,
                "reasoning": reasoning,
                "latency": latency,
                "timestamp": timestamp
            })