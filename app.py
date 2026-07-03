import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AMK Smart Pump AI Support", page_icon="💧")

# Setup AI (The API Key will be handled safely in the next step)
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Load the hardware code as the knowledge base
with open("source_code.cpp", "r") as f:
    knowledge_base = f.read()

st.title("💧 AMK Smart Pump Support AI")
st.subheader("Automated Troubleshooting & Documentation")

# Chat UI
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about errors, setup, or logic..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # The "Secret Sauce": The System Instruction
        context = f"""
        You are the technical expert for the AMK Smart Pump System. 
        Knowledge Source (Source Code):
        {knowledge_base}
        
        Instructions:
        1. Answer based ONLY on the logic in the source code.
        2. If the user asks in Myanmar language, answer in Myanmar language.
        3. Explain hardware pins (like Flow on Pin 18, Motor on Pin 8) when relevant.
        4. If they ask about a 'Dry Run', explain the Wait Seconds and Auto-Retry logic from the code.
        """
        
        response = model.generate_content([context, prompt])
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
