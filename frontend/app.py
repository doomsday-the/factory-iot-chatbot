import streamlit as st
import requests
import os

st.set_page_config(page_title="Factory Chatbot", page_icon="🏭", layout="centered")

# --- Tata Steel Professional Theme ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #F4F7FB;
    }

    /* Professional Header */
    .header-container {
        background: linear-gradient(135deg, #1B3A6B 0%, #29559B 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(27, 58, 107, 0.15);
        display: flex;
        align-items: center;
        gap: 16px;
    }
    
    .header-icon {
        background: rgba(255, 255, 255, 0.15);
        padding: 12px;
        border-radius: 10px;
        font-size: 1.5rem;
    }

    .header-text h1 {
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .header-text p {
        margin: 4px 0 0 0;
        font-size: 0.9rem;
        opacity: 0.85;
    }

    /* Chat Messages */
    .stChatMessage {
        background: white !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        margin-bottom: 12px;
        padding: 1.2rem !important;
    }

    /* Chat Input Container */
    .stChatInput > div {
        background: white !important;
        border: 1px solid #C1D0E3 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(27, 58, 107, 0.08) !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #88A0B8 !important;
    }

    /* Expander / SQL viewer */
    [data-testid="stExpander"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        background: #FAFCFF !important;
        box-shadow: none !important;
    }
    
    /* Hide top default padding */
    .block-container {
        padding-top: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class='header-container'>
    <div class='header-icon'>🏭</div>
    <div class='header-text'>
        <h1>Tata Steel IoT Intelligence</h1>
        <p>Enterprise Telemetry & Analytics Dashboard</p>
    </div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome. I am connected to the secure IoT telemetry database. You can query metrics for Welding, Gas Cutting, and Cladding operations. How can I assist you today?"}]

for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "sql" in message:
            with st.expander("View Generated SQL"):
                st.code(message["sql"], language="sql")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

if prompt := st.chat_input("Query shift metrics, downtime, or machine performance..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        placeholder.markdown("⏳ *Analyzing factory data...*")

        try:
            response = requests.post(f"{BACKEND_URL}/api/chat", json={"question": prompt}, timeout=60)
            if response.status_code == 200:
                data = response.json()
                answer = data["friendly_answer"]
                sql = data["sql"]
                
                placeholder.markdown(answer)
                with st.expander("View Generated SQL"):
                    st.code(sql, language="sql")
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "sql": sql
                })
            else:
                try:
                    err = response.json().get("detail", "Error")
                except:
                    err = response.text
                placeholder.markdown(f"❌ {err}")
                st.session_state.messages.append({"role": "assistant", "content": f"❌ {err}"})
        except Exception as e:
            placeholder.markdown(f"❌ Connection Error: {e}")
            st.session_state.messages.append({"role": "assistant", "content": f"❌ {e}"})
