import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AMK Smart Pump AI Support", page_icon="💧", layout="centered")

# Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# ---------------------------------------------------------
# MODEL SELECTION (Updated to 1.5-flash for stability)
# ---------------------------------------------------------
model = genai.GenerativeModel('gemini-1.5-flash') 

# ---------------------------------------------------------
# TRUE BLACK THEME (Mobile + Desktop Optimized)
# ---------------------------------------------------------
st.markdown("""
    <style>
        /* Force background to pure black */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
            background-color: #000000 !important;
            color: #FFFFFF !important;
        }

        /* Fix for Mobile Header/Top Bar */
        [data-testid="stHeader"] {
            background-color: rgba(0,0,0,0) !important;
        }

        /* Hide Streamlit elements */
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        [data-testid="stDecoration"] {display:none;}

        /* Chat Input Container Styling */
        [data-testid="stBottom"] {
            background-color: #000000 !important;
            border-top: 1px solid #222;
        }
        
        /* Input Box Styling */
        [data-testid="stChatInput"] {
            background-color: #1a1a1a !important;
            border-radius: 10px !important;
            border: 1px solid #333 !important;
        }

        /* Message Bubbles */
        [data-testid="stChatMessage"] {
            background-color: #111111 !important;
            border: 1px solid #222 !important;
            margin-bottom: 10px !important;
        }

        /* Text colors */
        p, li, h1, h2, h3, span {
            color: #FFFFFF !important;
        }

        /* Title & Caption Styling */
        .main-title {
            font-size: 1.5rem;
            font-weight: 700;
            text-align: center;
            margin-top: -30px;
            color: #FFFFFF;
        }
        .sub-caption {
            font-size: 0.8rem;
            color: #888;
            text-align: center;
            margin-bottom: 20px;
        }
    </style>
    
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Stable Support Engine • High Quota Mode</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# LOGIC & KNOWLEDGE BASE
# ---------------------------------------------------------

# Try to load source code for context
try:
    with open("source_code.cpp", "r") as f:
        knowledge_base = f.read()
except FileNotFoundError:
    knowledge_base = "No source code loaded."

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask about errors or setup..."):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant"):
        # We provide the knowledge base as context for every prompt
        full_prompt = f"System Context: {knowledge_base}\n\nUser Question: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            ai_response = response.text
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            st.error(f"Error: {str(e)}")
