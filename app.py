import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AMK Smart Pump AI Support", page_icon="💧")

# Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# ---------------------------------------------------------
# STABLE MODEL SELECTION (1,500 requests per day)
# ---------------------------------------------------------
# We use the most basic name to avoid 404 errors
model = genai.GenerativeModel('gemini-1.5-flash')
# ---------------------------------------------------------

# Custom Centered Styling
st.markdown(f"""
    <style>
        .block-container {{ padding-top: 1rem !important; padding-bottom: 0rem !important; }}
        .main-title {{ font-size: 1.3rem !important; font-weight: 800; text-align: center; width: 100%; }}
        .sub-caption {{ font-size: 0.72rem !important; color: #888; text-align: center; width: 100%; margin-bottom: 15px; }}
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Stable Support Engine (High Quota)</div>
    """, unsafe_allow_html=True)

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
        context = f"Technical Expert for AMK Pump. Source Code: {knowledge_base}\n\nUser Question: {prompt}"
        try:
            response = model.generate_content(context)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
