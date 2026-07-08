import streamlit as st
import google.generativeai as genai
import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. AI SETUP (Corrected Model Name)
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash') 

# 2. THE CARD LAYOUT HACK
st.markdown("""
    <style>
        /* 1. HIDE ALL NATIVE ELEMENTS */
        header, [data-testid="stHeader"], [data-testid="stToolbar"], footer, [data-testid="stDecoration"] {
            display: none !important;
            height: 0px !important;
            width: 0px !important;
        }

        /* 2. THE "LOCKED VIEWPORT" (Crucial) */
        /* This prevents the user from ever seeing or scrolling to the top icons */
        .stApp {
            background-color: #000000 !important;
            overflow: hidden !important; /* Disables page-level scrolling */
        }

        /* 3. THE CENTERED CHAT CARD */
        /* We build our own "window" that stays away from the edges */
        .main-card {
            background-color: #121212;
            border: 1px solid #333;
            border-radius: 20px;
            padding: 20px;
            margin: auto;
            max-width: 600px;
            height: 85vh; /* Sets a fixed height for the chat area */
            display: flex;
            flex-direction: column;
            box-shadow: 0px 10px 30px rgba(0,0,0,0.8);
        }

        /* 4. CHAT MESSAGE STYLING */
        [data-testid="stChatMessage"] {
            background-color: rgba(40, 40, 40, 0.5) !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 10px;
        }

        /* 5. FIX THE INPUT BAR TO THE BOTTOM OF THE CARD */
        [data-testid="stBottom"] {
            background-color: transparent !important;
        }
        
        .main-title { font-size: 1.2rem; font-weight: 800; text-align: center; color: #fff; margin-bottom: 5px; }
        .sub-caption { font-size: 0.7rem; color: #888; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# UI START
# ---------------------------------------------------------
st.markdown('<div class="main-title">💧 AMK Smart Pump Support AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-caption">Secure Support Engine • Gemini 1.5 Flash</div>', unsafe_allow_html=True)

# 3. USE A CONTAINER TO SIMULATE THE CARD
with st.container():
    # Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 4. CHAT LOGIC
    is_expired_status = st.query_params.get("expired", "False")
    user_id_from_url = st.query_params.get("id", "Unknown_User")

    if is_expired_status == "True":
        st.error("🛑 License Expired / လိုင်စင်သက်တမ်းကုန်ဆုံးနေပါသည်")
        st.stop()

    if prompt := st.chat_input("Ask about errors or setup..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            context = f"ROLE: Support for AMK Smart Automation. PASSWORDS: PROTECTED. LANG: MYANMAR."
            history = "".join([f"{m['role']}: {m['content']}\n" for m in st.session_state.messages[-4:]])
            
            try:
                response = model.generate_content(f"{context}\n{history}\nUSER: {prompt}", stream=True)
                full_res = st.write_stream(chunk.text for chunk in response if chunk.text)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
            except Exception as e:
                st.error("⚠️ System busy. Please try again.")
                if st.session_state.messages: st.session_state.messages.pop()
