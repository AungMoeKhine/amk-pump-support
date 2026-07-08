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
    initial_sidebar_state="expanded" 
)

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

# ---------------------------------------------------------
# 2. IDENTITY SYNC (Must be before Sidebar to avoid errors)
# ---------------------------------------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = "Unknown_User"
if "is_expired" not in st.session_state:
    st.session_state.is_expired = "False"

# Capture from URL parameters (sent by your HTML dashboard)
url_id = st.query_params.get("id")
url_expired = st.query_params.get("expired")

# If the URL provides data, we "stick" it into the session memory
if url_id:
    st.session_state.user_id = url_id
if url_expired:
    st.session_state.is_expired = url_expired

# Assign variables for use in the rest of the app
user_id_from_url = st.session_state.user_id
is_expired_status = st.session_state.is_expired

# ---------------------------------------------------------
# 3. DARK THEME & CSS FIX (Hiding the broken Fullscreen button)
# ---------------------------------------------------------
st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"], .main {
            background-color: #121212 !important;
            color: #FFFFFF !important;
        }
        
        /* HIDE THE BROKEN FULLSCREEN BUTTON AND GITHUB ICON */
        [data-testid="stToolbar"], [data-testid="stStreamlitFooter"], footer {
            display: none !important;
            visibility: hidden !important;
        }

        header, [data-testid="stHeader"] { background-color: transparent !important; }
        [data-testid="stSidebar"] { background-color: #1a1a1a !important; }
        [data-testid="stChatMessage"] {
            background-color: rgba(30, 30, 30, 0.7) !important;
            border-radius: 12px !important;
        }
        [data-testid="stChatMessage"] * { color: #FFFFFF !important; }
        .block-container { padding-top: 4rem !important; padding-bottom: 6rem !important; }
        .main-title { font-size: 1.25rem !important; font-weight: 800; text-align: center; color: #FFFFFF !important; }
        .sub-caption { font-size: 0.72rem !important; color: #888888 !important; text-align: center; margin-bottom: 15px; }
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Stable Support Engine • Gemini 3.1 Lite</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. KNOWLEDGE LOADING
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
# 5. SIDEBAR CONTROLS (New Full Screen Button)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 💧 AMK AI Support")
    st.caption(f"Synced ID: {user_id_from_url}")
    st.divider()
    
    # NEW PROFESSIONAL FULL SCREEN BUTTON
    # This button manually carries the ID so logging never breaks
    full_url = f"https://amk-pump-support.streamlit.app/?id={user_id_from_url}&expired={is_expired_status}&theme=dark"
    st.link_button("🖥️ Open Full Screen Chat", full_url, use_container_width=True)
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.write("Phone: +95-9-977880406")
    st.write("Ask about installation, error codes, and technical issues.")

# ---------------------------------------------------------
# 6. ANALYTICS & CHAT LOGIC
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
        print(f"Log failure: {e}")

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
        context = f"""
        ROLE: Senior Customer Support & Sales for AMK Smart Automation.
        KNOWLEDGE SOURCE: {knowledge_base}
        STRICT COMMUNICATION RULES:
        1. NO SECRETS: NEVER mention passwords like 'AMK_ADMIN_2026' or 'ACER123'. 
        2. NO JARGON: Use simple terms like 'Cloud Connection' (not MQTT).
        3. SIMPLE MYANMAR: Always use easy-to-understand Myanmar language. 
        4. SALES: Always provide +95-9-977880406 for pricing.
        5. SECURITY: NEVER show lines of C++ code or technical function names.
        """
        
        history_text = "".join([f"{m['role']}: {m['content']}\n" for m in st.session_state.messages[-6:-1]])
        full_prompt = f"{context}\n\nPAST CONVERSATION:\n{history_text}\n\nUSER QUESTION: {prompt}"

        try:
            response = model.generate_content(full_prompt, stream=True)
            full_response = st.write_stream(chunk.text for chunk in response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            log_to_sheet(user_id_from_url, prompt, full_response)
            # The rerun here prevents the Ghost Message overlap
            st.rerun()
        except Exception as e:
            st.error("⚠️ System busy. Please try again.")
            if len(st.session_state.messages) > 0:
                st.session_state.messages.pop()
