import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AMK Smart Pump AI Support", page_icon="💧")

# Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# ---------------------------------------------------------
# SAFE MODEL SELECTION (Fixes 404 and 429 Quota)
# ---------------------------------------------------------
@st.cache_resource
def get_working_model():
    try:
        # Get all models your API key is allowed to use
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 1. Try to find the Stable 1.5 Flash (1,500 requests/day)
        for target in ["models/gemini-1.5-flash", "models/gemini-1.5-flash-latest", "models/gemini-1.5-pro"]:
            if target in available:
                return target
        
        # 2. Fallback to whatever Google gives you (like 2.5 or 3.0)
        return available[0]
    except:
        return "gemini-1.5-flash" # Last resort guess

model_id = get_working_model()
model = genai.GenerativeModel(model_id)
# ---------------------------------------------------------

# Custom Styling
st.markdown(f"""
    <style>
        .block-container {{ padding-top: 1rem !important; padding-bottom: 0rem !important; }}
        .main-title {{ font-size: 1.3rem !important; font-weight: 800; text-align: center; width: 100%; }}
        .sub-caption {{ font-size: 0.72rem !important; color: #888; text-align: center; width: 100%; margin-bottom: 15px; }}
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Connected to: {model_id.replace('models/', '')}</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# CHAT LOGIC
# ---------------------------------------------------------

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
        context = f"Technical Expert for AMK Pump. Code: {knowledge_base}\nUser: {prompt}"
        try:
            response = model.generate_content(context)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"System Error: {str(e)}")
