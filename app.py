import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AMK Smart Pump AI Support", page_icon="💧")

# Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# ---------------------------------------------------------
# AUTO-DETECT CORRECT MODEL
# ---------------------------------------------------------
@st.cache_resource
def get_best_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if "models/gemini-1.5-flash" in available_models:
            return "models/gemini-1.5-flash"
        elif "models/gemini-1.5-pro" in available_models:
            return "models/gemini-1.5-pro"
        else:
            return available_models[0]
    except Exception as e:
        return "models/gemini-1.5-flash" 

best_model_name = get_best_model()
model = genai.GenerativeModel(best_model_name)

# ---------------------------------------------------------
# CUSTOM STYLING (Smaller, Centered, Fit for Mobile)
# ---------------------------------------------------------
st.markdown(f"""
    <style>
        /* 1. Reduce huge top space */
        .block-container {{ padding-top: 1rem !important; padding-bottom: 0rem !important; }}
        
        /* 2. Center and resize the Title */
        .main-title {{
            font-size: 1.3rem !important; 
            font-weight: 800;
            margin-bottom: 2px;
            letter-spacing: -0.5px;
            text-align: center;
            width: 100%;
        }}
        
        /* 3. Center and resize the Caption */
        .sub-caption {{
            font-size: 0.72rem !important;
            color: #888;
            margin-bottom: 15px;
            text-align: center;
            width: 100%;
        }}
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Connected via {best_model_name}</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# LOGIC & CHAT UI
# ---------------------------------------------------------

# Load the hardware code
with open("source_code.cpp", "r") as f:
    knowledge_base = f.read()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about errors or setup..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        context = f"""
        You are the technical expert for the AMK Smart Pump System. 
        Knowledge Source: {knowledge_base}
        
        Instructions:
        1. Answer based ONLY on the logic in the source code.
        2. Answer in Myanmar language if asked in Myanmar.
        3. Mention hardware pins when helpful.
        """
        
        try:
            response = model.generate_content(context + "\n\nUser: " + prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
