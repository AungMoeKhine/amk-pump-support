import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.5-flash')

# 3. ULTIMATE DARK THEME FIX (Targets Yellow Boxes specifically)
st.markdown("""
    <style>
        /* Force total black background on everything */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"], .main {
            background-color: #000000 !important;
        }

        /* HIDE ALL STREAMLIT UI ELEMENTS (Footer, Header, Line) */
        footer {display: none !important;}
        [data-testid="stFooter"] {display: none !important;}
        header {display: none !important;}
        [data-testid="stHeader"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}

        /* FIX MESSAGE DISPLAY (Yellow Box 1): Force White on ALL text levels */
        [data-testid="stChatMessage"] {
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
        }
        [data-testid="stChatMessage"] h1, 
        [data-testid="stChatMessage"] h2, 
        [data-testid="stChatMessage"] h3, 
        [data-testid="stChatMessage"] p, 
        [data-testid="stChatMessage"] li,
        [data-testid="stChatMessage"] div {
            color: #FFFFFF !important; /* Fixes the hard-to-see grey text */
        }

        /* FIX INPUT AREA (Yellow Box 2): Nuke the White Container */
        [data-testid="stBottom"] > div {
            background-color: #000000 !important;
            padding: 0px !important;
        }
        
        /* STYLE THE INPUT BOX: Dark Grey with White Text */
        [data-testid="stChatInput"] {
            border: 1px solid #444 !important;
            border-radius: 12px !important;
            background-color: #262626 !important;
        }
        [data-testid="stChatInput"] textarea {
            background-color: #262626 !important;
            color: #FFFFFF !important;
            caret-color: #FFFFFF !important;
        }
        /* Fix placeholder text color */
        [data-testid="stChatInput"] textarea::placeholder {
            color: #888888 !important;
        }

        /* Title and Padding */
        .block-container { 
            padding-top: 3.5rem !important; 
            padding-bottom: 8rem !important; 
        }
        .main-title {
            font-size: 1.2rem !important; 
            font-weight: 800;
            text-align: center;
            width: 100%;
            color: #FFFFFF !important;
            margin-bottom: 2px;
        }
        .sub-caption {
            font-size: 0.7rem !important;
            color: #888888 !important;
            text-align: center;
            width: 100%;
            margin-bottom: 15px;
        }
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Connected via Gemini 3.5 Frontier (Preview Quota)</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. CHAT LOGIC
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
            st.error(f"Error: {str(e)}")
