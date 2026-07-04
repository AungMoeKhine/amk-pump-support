import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AMK Smart Pump AI Support", page_icon="💧")

# Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# ---------------------------------------------------------
# FRONTIER MODEL SELECTION (Matching your Gemini 3 account)
# ---------------------------------------------------------
# We use the specific 3.5 model from your available list
model = genai.GenerativeModel('gemini-3.5-flash')
# ---------------------------------------------------------

# ---------------------------------------------------------
# CUSTOM STYLING (Fixed Cut-off Issue)
# ---------------------------------------------------------
st.markdown(f"""
    <style>
        /* Increase padding so title doesn't hide behind the top bar */
        .block-container {{ 
            padding-top: 3.5rem !important; 
            padding-bottom: 1rem !important; 
        }}
        
        .main-title {{
            font-size: 1.3rem !important; 
            font-weight: 800;
            margin-bottom: 2px;
            letter-spacing: -0.5px;
            text-align: center;
            width: 100%;
            color: white !important;
        }}
        
        .sub-caption {{
            font-size: 0.72rem !important;
            color: #AAAAAA !important;
            margin-bottom: 15px;
            text-align: center;
            width: 100%;
        }}
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Connected via Gemini 3.5 Frontier (Preview Quota)</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# LOGIC & CHAT UI
# ---------------------------------------------------------

# Load the hardware code knowledge
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
        # The Secret Sauce: System Instruction + User Prompt
        context = f"Technical Expert for AMK Pump. Code: {knowledge_base}\n\nUser Question: {prompt}"
        try:
            response = model.generate_content(context)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"System Error: {str(e)}")
