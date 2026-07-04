import streamlit as st
import google.generativeai as genai
import os

# Page Config
st.set_page_config(page_title="AMK Smart Pump AI Support", page_icon="💧")

# Setup AI 
# Ensure your Streamlit Secret is named "GEMINI_API_KEY"
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# ---------------------------------------------------------
# DYNAMIC MODEL PICKER (Updated for Gemini 3.x)
# ---------------------------------------------------------
@st.cache_resource
def get_active_model():
    try:
        # Get list of models available to your specific API Key
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority order based on your screenshot
        priority = [
            "models/gemini-3.5-flash",
            "models/gemini-3.1-flash-lite",
            "models/gemini-3-flash",
            "models/gemini-1.5-flash"
        ]
        
        for p in priority:
            if p in available:
                return genai.GenerativeModel(p)
        
        # Fallback to the first available model if none of the above match
        return genai.GenerativeModel(available[0])
    except Exception:
        # Hard fallback to the newest model in your screenshot
        return genai.GenerativeModel("models/gemini-3.5-flash")

model = get_active_model()

# ---------------------------------------------------------
# CUSTOM STYLING (Mobile Friendly)
# ---------------------------------------------------------
st.markdown(f"""
    <style>
        .block-container {{ padding-top: 1rem !important; padding-bottom: 0rem !important; }}
        .main-title {{
            font-size: 1.3rem !important; 
            font-weight: 800;
            margin-bottom: 2px;
            letter-spacing: -0.5px;
            text-align: center;
            width: 100%;
        }}
        .sub-caption {{
            font-size: 0.72rem !important;
            color: #888;
            margin-bottom: 15px;
            text-align: center;
            width: 100%;
        }}
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Connected via {model.model_name.split('/')[-1].replace('-', ' ').title()}</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# KNOWLEDGE BASE LOADING
# ---------------------------------------------------------
try:
    with open("source_code.cpp", "r") as f:
        knowledge_base = f.read()
except FileNotFoundError:
    knowledge_base = "Source code file not found. Please upload source_code.cpp."

# ---------------------------------------------------------
# CHAT LOGIC
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask about errors or setup..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        context = f"""
        You are the technical expert for the AMK Smart Pump System. 
        Knowledge Source (Hardware Logic): 
        {knowledge_base}
        
        Instructions:
        1. Answer based ONLY on the logic in the source code provided.
        2. Answer in Myanmar language if asked in Myanmar.
        3. Mention specific hardware pins when troubleshooting.
        """
        
        try:
            # Using the stream method for better UI feel
            response = model.generate_content(context + "\n\nUser Question: " + prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Model Error: {str(e)}")
            st.info("Tip: Check if your API Key has access to " + model.model_name)
