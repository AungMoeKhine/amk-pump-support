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
model = genai.GenerativeModel('gemini-1.5-flash')

# ---------------------------------------------------------
# 2. TRANSLATION DICTIONARY (This makes the UI change)
# ---------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "English"

# Define all UI text in both languages
texts = {
    "English": {
        "title": "💧 AMK Smart Pump Support AI",
        "caption": "Stable Support Engine • Authorized Access Only",
        "sidebar_title": "💧 AMK AI Support",
        "clear_btn": "🗑️ Clear Chat History",
        "contact": "Phone",
        "instruction": "Ask about installation, error codes, pricing, and solving technical issues.",
        "input_placeholder": "Ask about errors or setup...",
        "expired": "🛑 License Expired",
        "busy": "⚠️ System busy."
    },
    "Myanmar": {
        "title": "💧 AMK စမတ်ပန့် အကူအညီပေးရေး AI",
        "caption": "တည်ငြိမ်သောစနစ် • ခွင့်ပြုချက်ရှိသူများသာ",
        "sidebar_title": "💧 AMK AI အကူအညီ",
        "clear_btn": "🗑️ ပြောဆိုမှုမှတ်တမ်းဖျက်ရန်",
        "contact": "ဖုန်းနံပါတ်",
        "instruction": "တပ်ဆင်ခြင်း၊ အမှားကုဒ်များ၊ ဈေးနှုန်းနှင့် နည်းပညာပိုင်းဆိုင်ရာများကို မေးမြန်းနိုင်ပါသည်။",
        "input_placeholder": "သိလိုသည်များကို မေးမြန်းပါ...",
        "expired": "🛑 လိုင်စင်သက်တမ်းကုန်ဆုံးနေပါသည်",
        "busy": "⚠️ စနစ် အလုပ်များနေပါသည်။"
    }
}

L = texts[st.session_state.lang] # Shortcut for current language

# ---------------------------------------------------------
# 3. ULTIMATE TRANSPARENCY SETUP
# ---------------------------------------------------------
st.markdown(f"""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainViewContainer"], 
        .main, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stBottom"] {{
            background-color: transparent !important;
        }}
        [data-testid="stChatMessage"] {{
            background-color: rgba(30, 30, 30, 0.8) !important;
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .main-title {{ font-size: 1.25rem !important; font-weight: 800; text-align: center; color: #FFFFFF !important; }}
        .sub-caption {{ font-size: 0.72rem !important; color: #888888 !important; text-align: center; margin-bottom: 15px; }}
    </style>
    <div class="main-title">{L['title']}</div>
    <div class="sub-caption">{L['caption']}</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. SIDEBAR (With Language Selector)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(f"## {L['sidebar_title']}")
    
    # LANGUAGE SELECTOR TOGGLE
    st.session_state.lang = st.radio("Language / ဘာသာစကား", ["English", "Myanmar"], horizontal=True)
    
    st.divider()
    if st.button(L['clear_btn'], use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.write(f"{L['contact']}: +95-9-977880406")
    st.write(L['instruction'])

# ---------------------------------------------------------
# 5. KNOWLEDGE & ANALYTICS (Kept exactly as previous)
# ---------------------------------------------------------
@st.cache_data
def load_knowledge_data():
    try:
        with open("source_code.cpp", "r") as f: code_data = f.read(10000)
        with open("manual.txt", "r") as f: manual_data = f.read()
        return f"TECHNICAL_SPECS:\n{code_data}\n\nTROUBLESHOOTING_MANUAL:\n{manual_data}"
    except Exception: return "Knowledge base unavailable."

knowledge_base = load_knowledge_data()

def log_to_sheet(user_id, question, answer):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection, ttl=0)
        new_row = pd.DataFrame([{
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Cloud_ID": user_id, "User_Question": question, "AI_Response": answer, "Error_Code": "None" 
        }])
        existing_data = conn.read(worksheet="Analytics", ttl=0)
        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(data=updated_data, worksheet="Analytics")
    except Exception: pass

# ---------------------------------------------------------
# 6. CHAT LOGIC
# ---------------------------------------------------------
is_expired_status = st.query_params.get("expired", "False")
user_id_from_url = st.query_params.get("id", "Unknown_User")

if is_expired_status == "True":
    st.error(L['expired'])
    st.stop() 

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(L['input_placeholder']):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # AI Logic: Detect language automatically but follow "Do's and Don'ts"
        context = f"""
        ROLE: Senior Support Engineer for AMK Smart Pumps. 
        KNOWLEDGE: {knowledge_base}
        LANGUAGE: Respond in the language used by the user ({st.session_state.lang} preferred).
        SECURITY: Only answer from knowledge. If unknown, provide +95-9-977880406.
        """
        history_text = "".join([f"{m['role']}: {m['content']}\n" for m in st.session_state.messages[-5:]])
        full_prompt = f"{context}\n\nUSER: {prompt}"

        try:
            response = model.generate_content(full_prompt, stream=True)
            full_response = st.write_stream(chunk.text for chunk in response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            log_to_sheet(user_id_from_url, prompt, full_response)
        except Exception:
            st.error(L['busy'])
