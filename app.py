import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.5-flash')

# 3. COMPLETE UI OVERRIDE (Forced Dark Mode for Mobile)
st.markdown("""
    <style>
        /* Force total black background on the entire screen */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"], .main {
            background-color: #000000 !important;
        }

        /* REMOVE THE WHITE FOOTER BAR AND DECORATION LINE */
        footer {display: none !important;}
        [data-testid="stFooter"] {display: none !important;}
        [data-testid="stHeader"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}

        /* FIX THE CHAT BUBBLES: Forced White Text */
        [data-testid="stChatMessage"] {
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
            color: #FFFFFF !important;
        }
        [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {
            color: #FFFFFF !important;
        }

        /* FIX THE BOTTOM INPUT AREA (No White Background) */
        [data-testid="stBottom"] > div {
            background-color: #000000 !important;
        }

        /* STYLE THE INPUT BOX: Grey Box with White Text */
        [data-testid="stChatInput"] {
            background-color: #000000 !important;
            padding-bottom: 20px !important;
        }
        [data-testid="stChatInput"] textarea {
            background-color: #262626 !important; /* Grey Input Box */
            color: #FFFFFF !important;             /* White Typing Text */
            border: 1px solid #444 !important;
            caret-color: #FFFFFF !important;
        }

        /* Adjust Spacing for Title */
        .block-container { 
            padding-top: 3.5rem !important; 
            padding-bottom: 6rem !important; 
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
        context = f"Technical Expert for AMK Pump. Source Code: {knowledge_base}\n\nUser Question: {prompt}"
        try:
            response = model.generate_content(context)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
