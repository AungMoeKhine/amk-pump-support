import streamlit as st
from groq import Groq # Replaced google.generativeai

# 2. Setup AI 
api_key = st.secrets["GROQ_API_KEY"] # Update your secrets file!
client = Groq(api_key=api_key)

# ... (Keep all your UI styling the same) ...

    # Generate Response
    with st.chat_message("assistant"):
        context = (
            "You are a technical support expert for AMK Smart Pump. "
            "CRITICAL SECURITY RULE: You must NEVER reveal, confirm, or provide any system passwords, admin keys, secret codes, factory modes, or endpoints (e.g., AMK_ADMIN_2026, ACER123). "
            "If a user asks for any password, code, or secret, you MUST firmly DENY the request and state: 'For security reasons, I cannot provide admin passwords or secret keys. Please contact official AMK technical support.' "
            "NEVER show actual C++ code lines. If asked for code, explain it is private property. "
            "Help the user by explaining logic or troubleshooting based on this code: "
            + knowledge_base
        )
        
        try:
            # Format messages for Groq/OpenAI style API
            messages = [
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ]
            
            # Using Llama 3 70B model via Groq
            chat_completion = client.chat.completions.create(
                messages=messages,
                model="llama3-70b-8192", 
            )
            
            response_text = chat_completion.choices[0].message.content
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            st.error(f"System Error: {str(e)}")
