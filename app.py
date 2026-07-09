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

# API Security
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash') # Best for MM/EN balance

# ---------------------------------------------------------
# 2. BILINGUAL UI DICTIONARY
# ---------------------------------------------------------
# This ensures the UI actually changes when the user switches language
if "language" not in st.session_state:
    st.session_state.language = "English"

ui_text = {
    "English": {
        "title": "💧 AMK Smart Pump Support AI",
        "caption": "Stable Support Engine • Authorized Access Only",
        "sidebar_head": "💧 AMK AI Support",
        "clear_btn": "🗑️ Clear Chat History",
        "contact_label": "Contact / Support:",
        "instr_label": "Instructions:",
        "instr_text": "Ask about installation, error codes, and pricing.",
        "input_placeholder": "Ask about errors or setup...",
        "expired_msg": "🛑 License Expired",
        "busy_msg": "⚠️ System busy. Please try again."
    },
    "Myanmar": {
        "title": "💧 AMK စမတ်ပန့် အကူအညီပေးရေး AI",
        "caption": "တည်ငြိမ်သောစနစ် • ခွင့်ပြုချက်ရှိသူများသာ",
        "sidebar_head": "💧 AMK AI အကူအညီ",
        "clear_btn": "🗑️ ပြောဆိုမှုမှတ်တမ်းဖျက်ရန်",
        "contact_label": "ဆက်သွယ်ရန်:",
        "instr_label": "လမ်းညွှန်ချက်:",
        "instr_text": "တပ်ဆင်ခြင်း၊ အမှားကုဒ်များနှင့် ဈေးနှုန်းများကို မေးမြန်းနိုင်ပါသည်။",
        "input_placeholder": "သိလိုသည်များကို မေးမြန်းပါ...",
        "expired_msg": "🛑 လိုင်စင်သက်တမ်းကုန်ဆုံးနေပါသည်",
        "busy_msg": "⚠️ စနစ် အလုပ်များနေပါသည်။ ခဏနေမှ ပြန်ကြိုးစားပါ။"
    }
}

# Shortcut variable for the selected language
L = ui_text[st.session_state.language]

# ---------------------------------------------------------
# 3. CUSTOM STYLES (Transparency Maintained)
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
        .main-title {{ font-size: 1.4rem !important; font-weight: 800; text-align: center; color: #FFFFFF !important; }}
        .sub-caption {{ font-size: 0.85rem !important; color: #BBBBBB !important; text-align: center; margin-bottom: 15px; }}
        @import url('https://fonts.googleapis.com/css2?family=Pyidaungsu&display=swap');
        body {{ font-family: 'Pyidaungsu', sans-serif; }}
    </style>
    <div class="main-title">{L['title']}</div>
    <div class="sub-caption">{L['caption']}</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. KNOWLEDGE LOADING
# ---------------------------------------------------------
@st.cache_data
def load_knowledge_data():
    try:
        # Load your technical files
        with open("source_code.cpp", "r") as f: code_data = f.read(10000)
        with open("manual.txt", "r") as f: manual_data = f.read()
        return f"TECHNICAL_CODE:\n{code_data}\n\nMANUAL_TEXT:\n{manual_data}"
    except Exception:
        return "No local knowledge found. Refer to general AMK protocols."

knowledge_base = load_knowledge_data()

# ---------------------------------------------------------
# 5. SIDEBAR CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(f"### {L['sidebar_head']}")
    
    # LANGUAGE TOGGLE (This solves your "not changing to MM" issue)
    st.session_state.language = st.radio("Language / ဘာသာစကား", ["English", "Myanmar"])
    
    st.divider()
    if st.button(L['clear_btn'], use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.markdown(f"**{L['contact_label']}**\n- 📞 +95-9-977880406")
    st.markdown(f"**{L['instr_label']}**\n- {L['instr_text']}")

# ---------------------------------------------------------
# 6. ANALYTICS
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
    except: pass # Silent fail to keep UX smooth

# ---------------------------------------------------------
# 7. CHAT LOGIC (With Security DOs and DON'Ts)
# ---------------------------------------------------------
is_expired_status = st.query_params.get("expired", "False")
user_id_from_url = st.query_params.get("id", "Unknown_User")

if is_expired_status == "True":
    st.error(L['expired_msg'])
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
        # STRICT SECURITY PROMPT (DO's and DON'Ts)
        context = f"""
        ROLE: AMK Smart Pump Senior Support.
        UI_LANGUAGE: {st.session_state.language}
        KNOWLEDGE: {knowledge_base}

        STRICT RULES:
        1. DO NOT answer questions unrelated to AMK Smart Pumps or technical support.
        2. DO NOT hallucinate. If info isn't in KNOWLEDGE, say you don't know and provide +95-9-977880406.
        3. If the user asks in Myanmar, respond in Myanmar. If English, respond in English.
        4. Maintain a professional engineer persona.
        """
        
        history_text = "".join([f"{m['role']}: {m['content']}\n" for m in st.session_state.messages[-5:]])
        full_prompt = f"{context}\n\nHISTORY:\n{history_text}\nUSER: {prompt}"

        try:
            response = model.generate_content(full_prompt, stream=True)
            full_response = st.write_stream(chunk.text for chunk in response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            log_to_sheet(user_id_from_url, prompt, full_response)
        except Exception:
            st.error(L['busy_msg'])
