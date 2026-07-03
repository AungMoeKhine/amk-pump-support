import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AMK Smart Pump AI Support", page_icon="💧")

# Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# CHANGE: Use 1.5-pro (more stable) and add the models/ prefix
model = genai.GenerativeModel('models/gemini-1.5-pro')

# Load the hardware code
with open("source_code.cpp", "r") as f:
    knowledge_base = f.read()

st.title("💧 AMK Smart Pump Support AI")
st.subheader("Automated Troubleshooting & Documentation")

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
        # The Instruction
        system_instruction = f"""
        You are the technical expert for the AMK Smart Pump System. 
        Knowledge Source (Source Code):
        {knowledge_base}
        
        Instructions:
        1. Answer based ONLY on the logic in the source code.
        2. If the user asks in Myanmar language, answer in Myanmar language.
        3. Explain hardware pins (like Flow on Pin 18, Motor on Pin 8) when relevant.
        4. If they ask about a 'Dry Run', explain the Wait Seconds and Auto-Retry logic from the code.
        """
        
        # CHANGE: Send as a single string instead of a list for better reliability
        full_query = system_instruction + "\n\nUser Question: " + prompt
        
        try:
            response = model.generate_content(full_query)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"AI Connection Error: {str(e)}")
