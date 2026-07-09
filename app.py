import streamlit as st
import google.generativeai as genai
import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ---------------------------------------------------------
# 1. PAGE CONFIG & AI SETUP
# ---------------------------------------------------------
st.set_page_config(
    page_title="AMK AI Support", 
    page_icon="💧",
    initial_sidebar_state="expanded" # This ensures sidebar starts open
)

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

# ---------------------------------------------------------
# 2. ULTIMATE TRANSPARENCY SETUP
# ---------------------------------------------------------
st.markdown("""
    <style>
        /* 1. Make the entire app and all containers transparent */
        .stApp, 
        [data-testid="stAppViewContainer"], 
        [data-testid="stMainViewContainer"], 
        .main, 
        [data-testid="stHeader"], 
        [data-testid="stToolbar"],
        [data-testid="stBottom"] {
            background-color: transparent !important;
            background: transparent !important;
        }

        /* 2. Specifically make the sidebar arrow container transparent */
        [data-testid="collapsedControl"] {
            background-color: transparent !important;
            background: transparent !important;
            top: 10px; /* Adjust this to align with your website header if needed */
        }

        /* 3. Ensure the chat input area at the bottom doesn't have a solid background */
        [data-testid="stBottom"] > div {
            background-color: transparent !important;
        }

        /* 4. Keep the Chat Messages readable (semi-transparent dark) */
        [data-testid="stChatMessage"] {
            background-color: rgba(30, 30, 30, 0.8) !important;
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* 5. Adjust padding so your title "AMK Smart Pump..." starts lower */
        .block-container {
            padding-top: 4rem !important; /* Increase this if the title is still too high */
        }

        /* Hide Streamlit decoration bar at the very top */
        [data-testid="stDecoration"] {
            display: none !important;
        }

        /* Title and Caption Styles */
        .main-title { 
            font-size: 1.25rem !important; 
            font-weight: 800; 
            text-align: center; 
            width: 100%; 
            color: #FFFFFF !important; 
        }
        .sub-caption { 
            font-size: 0.72rem !important; 
            color: #888888 !important; 
            text-align: center; 
            width: 100%; 
            margin-bottom: 15px; 
        }
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Stable Support Engine • Authorized Access Only</div>
    """, unsafe_allow_html=True)
# ---------------------------------------------------------
# 3. KNOWLEDGE LOADING
# ---------------------------------------------------------
@st.cache_data
def load_knowledge_data():
    try:
        with open("source_code.cpp", "r") as f: code_data = f.read(10000)
        with open("manual.txt", "r") as f: manual_data = f.read()
        return f"TECHNICAL_SPECS:\n{code_data}\n\nTROUBLESHOOTING_MANUAL:\n{manual_data}"
    except Exception:
        return "Knowledge base unavailable."

knowledge_base = load_knowledge_data()

# ---------------------------------------------------------
# 4. SIDEBAR CONTROLS (Now visible again)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 💧 AMK AI Support")
    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.write("Phone: +95-9-977880406")
    st.write("Ask about installation, error codes, pricing, and solving technical issues.")

# ---------------------------------------------------------
# 5. ANALYTICS FUNCTION
# ---------------------------------------------------------
def log_to_sheet(user_id, question, answer):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection, ttl=0)
        new_row = pd.DataFrame([{
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Cloud_ID": user_id,
            "User_Question": question,
            "AI_Response": answer,
            "Error_Code": "None" 
        }])
        existing_data = conn.read(worksheet="Analytics", ttl=0)
        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(data=updated_data, worksheet="Analytics")
    except Exception as e:
        print(f"Analytics failure: {e}")

# ---------------------------------------------------------
# 6. CHAT LOGIC
# ---------------------------------------------------------
is_expired_status = st.query_params.get("expired", "False")
user_id_from_url = st.query_params.get("id", "Unknown_User")

if is_expired_status == "True":
    st.error("🛑 License Expired / လိုင်စင်သက်တမ်းကုန်ဆုံးနေပါသည်")
    st.stop() 

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
        context = f"ROLE: Senior Support. KNOWLEDGE: {knowledge_base}"
        history_text = "".join([f"{m['role']}: {m['content']}\n" for m in st.session_state.messages[-6:-1]])
        full_prompt = f"{context}\n\nPAST CONVERSATION:\n{history_text}\n\nUSER QUESTION: {prompt}"

        try:
            response = model.generate_content(full_prompt, stream=True)
            full_response = st.write_stream(chunk.text for chunk in response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            log_to_sheet(user_id_from_url, prompt, full_response)
        except Exception as e:
            st.error("⚠️ System busy.") 
