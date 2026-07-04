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
# TOTAL DARK MODE STYLING (Fixes White Bottom & Input Bar)
# ---------------------------------------------------------
st.markdown(f"""
    <style>
        /* 1. Force the entire app background to Black */
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"] {{
            background-color: #000000 !important;
            color: #FFFFFF !important;
        }}

        /* 2. Fix the White Bottom Input area */
        [data-testid="stBottom"] > div {{
            background-color: #000000 !important;
        }}

        /* 3. Style the Chat Input box itself */
        [data-testid="stChatInput"] textarea {{
            background-color: #1E1E1E !important;
            color: #FFFFFF !important;
            border: 1px solid #333333 !important;
        }}

        /* 4. Hide the "Built with Streamlit" footer for a cleaner look */
        footer {{ visibility: hidden !important; }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}

        /* 5. Adjust padding so title sits correctly */
        .block-container {{ 
            padding-top: 3rem !important; 
            padding-bottom: 5rem !important; 
        }}
        
        /* 6. Title and Caption Centering */
        .main-title {{
            font-size: 1.2rem !important; 
            font-weight: 800;
            text-align: center;
            width: 100%;
            color: #FFFFFF !important;
            margin-bottom: 2px;
        }}
        .sub-caption {{
            font-size: 0.7rem !important;
            color: #AAAAAA !important;
            text-align: center;
            width: 100%;
            margin-bottom: 15px;
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
