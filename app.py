import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.5-flash')

# 3. THE "COMPUTER-LIKE" MOBILE OVERRIDE
st.markdown("""
    <style>
        /* Force Black Background on everything (Mobile + Desktop) */
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"], .main {
            background-color: #000000 !important;
        }

        /* 1. REMOVE THE WHITE FOOTER (Built with Streamlit) */
        footer { display: none !important; }
        [data-testid="stFooter"] { display: none !important; }
        [data-testid="stDecoration"] { display: none !important; }

        /* 2. FIX THE WHITE BOX AROUND INPUT ON MOBILE */
        [data-testid="stBottom"] > div {
            background-color: #000000 !important;
            padding-bottom: 20px !important;
        }

        /* 3. MAKE THE INPUT BOX LOOK LIKE COMPUTER (Grey) */
        [data-testid="stChatInput"] {
            background-color: #1E1E1E !important;
            border: 1px solid #333 !important;
            border-radius: 15px !important;
        }
        [data-testid="stChatInput"] textarea {
            background-color: transparent !important;
            color: #FFFFFF !important;
        }

        /* 4. FIX MESSAGE COLORS: White text on dark grey bubbles */
        [data-testid="stChatMessage"] {
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
            border-radius: 15px !important;
        }
        [data-testid="stChatMessage"] h1, [data-testid="stChatMessage"] h2, 
        [data-testid="stChatMessage"] h3, [data-testid="stChatMessage"] p, 
        [data-testid="stChatMessage"] li {
            color: #FFFFFF !important;
        }

        /* Adjust Title Spacing */
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
