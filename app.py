import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.5-flash')

# 3. THE "DARK MODE FOREVER" OVERRIDE
st.markdown("""
    <style>
        /* Force Black Background everywhere */
        html, body, .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stBottom"] {
            background-color: #000000 !important;
            color: #FFFFFF !important;
        }

        /* Kill the White/Grey Streamlit elements */
        footer, header, [data-testid="stHeader"], [data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Fix User/AI messages to be Dark Grey with White Text */
        [data-testid="stChatMessage"] {
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
            color: #FFFFFF !important;
        }
        [data-testid="stChatMessage"] * {
            color: #FFFFFF !important;
        }

        /* TARGET THE MOBILE INPUT CONTAINER specifically */
        [data-testid="stBottom"] > div {
            background-color: #000000 !important;
            padding: 10px !important;
        }

        /* Target the typing box container */
        [data-testid="stChatInput"] {
            background-color: #262626 !important;
            border: 1px solid #444 !important;
            border-radius: 12px !important;
        }

        /* Target the actual text area where you type */
        [data-testid="stChatInput"] textarea {
            background-color: transparent !important;
            color: #FFFFFF !important;
            caret-color: #FFFFFF !important;
        }

        /* Header Styling */
        .block-container { padding-top: 2.5rem !important; padding-bottom: 6rem !important; }
        .main-title { font-size: 1.25rem !important; font-weight: 800; text-align: center; width: 100%; color: #FFFFFF !important; }
        .sub-caption { font-size: 0.72rem !important; color: #888888 !important; text-align: center; width: 100%; margin-bottom: 15px; }
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Forced Dark Mode • Gemini 3.5 Frontier</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. CHAT LOGIC
# ---------------------------------------------------------
try:
    with open("source_code.cpp", "r") as f:
        code_data = f.read(10000)
    with open("manual.txt", "r") as f:
        manual_data = f.read()
    knowledge_base = f"CODE:\n{code_data}\n\nMANUAL:\n{manual_data}"
except:
    knowledge_base = "Knowledge unavailable."

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
        context = "Technical Support for AMK Smart Pump. Rule: No passwords/code sharing. Knowledge: " + knowledge_base
        try:
            response = model.generate_content(context + "\n\nUser Question: " + prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                st.error("⚠️ Daily question limit reached. Please retry in 24 hours.")
            else:
                st.error("⚠️ System busy. Please refresh.")
            if len(st.session_state.messages) > 0:
                st.session_state.messages.pop()
