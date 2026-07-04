import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AMK Smart Pump AI Support", page_icon="💧")

# Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# ---------------------------------------------------------
# MODEL SELECTION (Kept exactly as you requested)
# ---------------------------------------------------------
model = genai.GenerativeModel('gemini-3.5-flash') 
# ---------------------------------------------------------

# ---------------------------------------------------------
# COLOR & UI FIXES (Matches Computer and Mobile)
# ---------------------------------------------------------
st.markdown(f"""
    <style>
        /* 1. Force Black Background on everything */
        html, body, .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stBottom"] {{
            background-color: #000000 !important;
            color: #FFFFFF !important;
        }}

        /* 2. Remove White Footer and Top Decoration */
        footer {{ visibility: hidden !important; height: 0px !important; }}
        [data-testid="stFooter"] {{ display: none !important; }}
        [data-testid="stDecoration"] {{ display: none !important; }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0) !important; }}

        /* 3. Fix the Bottom Input container (Delete White background) */
        [data-testid="stBottom"] > div {{
            background-color: #000000 !important;
            padding-bottom: 20px !important;
        }}

        /* 4. Style the Input Box: Grey background with White text */
        [data-testid="stChatInput"] {{
            background-color: #262626 !important;
            border: 1px solid #444 !important;
            border-radius: 12px !important;
        }}
        [data-testid="stChatInput"] textarea {{
            background-color: #262626 !important;
            color: #FFFFFF !important;
            caret-color: #FFFFFF !important;
        }}

        /* 5. Message bubbles color fix */
        [data-testid="stChatMessage"] {{
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
            border-radius: 15px !important;
        }}
        [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li, [data-testid="stChatMessage"] h3 {{
            color: #FFFFFF !important;
        }}

        /* 6. Spacing and Title Styling */
        .block-container {{ padding-top: 2rem !important; padding-bottom: 6rem !important; }}
        .main-title {{
            font-size: 1.3rem !important; 
            font-weight: 800;
            text-align: center;
            width: 100%;
            color: #FFFFFF !important;
            margin-bottom: 2px;
        }}
        .sub-caption {{
            font-size: 0.72rem !important;
            color: #888888 !important;
            text-align: center;
            width: 100%;
            margin-bottom: 15px;
        }}
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Stable Support Engine (High Quota)</div>
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
    with st.chat_message("user"
