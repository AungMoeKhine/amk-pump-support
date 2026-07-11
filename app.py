import streamlit.components.v1 as components
import streamlit as st
import google.generativeai as genai
import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ---------------------------------------------------------
# 1. PAGE CONFIG & AI SETUP
# ---------------------------------------------------------

LOGO_URL = "https://raw.githubusercontent.com/AungMoeKhine/smart_water_pump-control/main/logo.png"

st.set_page_config(
    page_title="AMK AI Support", 
    page_icon="💧",
    initial_sidebar_state="expanded" # Keeps sidebar visible
)

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

# ---------------------------------------------------------
# 2. BILINGUAL UI & LANGUAGE LOGIC
# ---------------------------------------------------------
ui = {
    "English": {
        "title": "💧 AMK Smart Pump Support AI",
        "caption": "Official Technical & Sales Support",
        "sidebar_head": "💧 AMK AI Support",
        "clear_btn": "🗑️ Clear Chat History",
        "contact": "Contact",
        "instr": "Ask about pricing, features, or error codes.",
        "placeholder": "Type your query or request...",
        "expired": "🛑 License Expired",
        "busy": "⚠️ System busy."
    },
    "Myanmar": {
        "title": "💧 AMK စမတ်ပန့် အကူအညီပေးရေး AI",
        "caption": "နည်းပညာနှင့် အရောင်းဆိုင်ရာ အကူအညီ",
        "sidebar_head": "💧 AMK AI အကူအညီ",
        "clear_btn": "🗑️ ပြောဆိုမှုမှတ်တမ်းဖျက်ရန်",
        "contact": "ဆက်သွယ်ရန်",
        "instr": "ဈေးနှုန်း၊ အချက်အလက်နှင့် အမှားကုဒ်များကို မေးမြန်းပါ။",
        "placeholder": "သိလိုသည်များကို မေးမြန်းပါ...",
        "expired": "🛑 လိုင်စင်သက်တမ်းကုန်ဆုံးနေပါသည်",
        "busy": "⚠️ စနစ် အလုပ်များနေပါသည်။"
    }
}

# Accessing language from session state immediately
if "language" not in st.session_state:
    st.session_state.language = "English"

L = ui[st.session_state.language]

# ---------------------------------------------------------
# 3. UI STYLING & ROBUST HAPTIC FEEDBACK
# ---------------------------------------------------------
st.markdown(f"""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainViewContainer"], 
        .main, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stBottom"] {{
            background-color: transparent !important;
            background: transparent !important;
        }}
        [data-testid="stChatMessage"] {{
            background-color: rgba(30, 30, 30, 0.8) !important;
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            overflow-wrap: break-word !important;
            word-wrap: break-word !important;
            word-break: break-word !important;
        }}
        [data-testid="stChatMessageContent"] {{
            line-height: 1.6 !important;
        }}
        [data-testid="stDecoration"] {{ display: none !important; }}
        .block-container {{ padding-top: 4rem !important; }}
        
        .header-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding-bottom: 5px;
        }}
        .main-logo {{
            width: 42px;
            height: 42px;
            border-radius: 50%;
            border: 2px solid rgba(0, 210, 255, 0.3);
        }}
        .main-title {{ 
            font-size: 0.88rem !important; 
            font-weight: 800; 
            color: #FFFFFF !important; 
            white-space: nowrap; 
            letter-spacing: -1px; 
            margin: 0;
            line-height: 1.2;
        }}
        
        .sub-caption {{ font-size: 0.72rem !important; color: #888888 !important; text-align: center; margin-bottom: 15px; margin-left: 20px; }}
        @import url('https://fonts.googleapis.com/css2?family=Pyidaungsu&display=swap');
        body {{ font-family: 'Pyidaungsu', sans-serif; }}
    </style>
    <div class="header-container">
        <img src="{LOGO_URL}" class="main-logo">
        <div class="main-title">{L['title']}</div>
    </div>
    <div class="sub-caption">{L['caption']}</div>
    """, unsafe_allow_html=True)

# This component injects JavaScript into the parent window to catch all clicks
components.html(
    """
    <script>
    const executeHaptic = () => {
        if (window.navigator && window.navigator.vibrate) {
            window.navigator.vibrate(60); // 60ms vibration
        }
    };

    // Use window.parent to catch clicks outside the iframe (Streamlit's main UI)
    const doc = window.parent.document;
    
    doc.addEventListener('click', (e) => {
        // Target anything that looks like a button (radio buttons, chat send, clear history)
        const isButton = e.target.tagName === 'BUTTON' || 
                         e.target.closest('button') || 
                         e.target.closest('[role="radiogroup"]');
        
        if (isButton) {
            executeHaptic();
        }
    }, true);
    </script>
    """,
    height=0,
    width=0,
)

# ---------------------------------------------------------
# 4. KNOWLEDGE LOADING
# ---------------------------------------------------------
@st.cache_data
def load_knowledge_data():
    try:
        with open("source_code.cpp", "r") as f: code_data = f.read(10000)
        with open("manual.txt", "r") as f: manual_data = f.read()
        return f"TECHNICAL_CODE_CONTEXT:\n{code_data}\n\nSALES_AND_USER_MANUAL:\n{manual_data}"
    except Exception:
        return "Knowledge base unavailable."

knowledge_base = load_knowledge_data()

# ---------------------------------------------------------
# 5. SIDEBAR & CLEAR HISTORY
# ---------------------------------------------------------
def change_language():
    # This empty function triggers a rerun with the new session_state.language
    pass

with st.sidebar:

    st.image(LOGO_URL, width=80)

    st.markdown(f"### {L['sidebar_head']}")
    
    # Language Switcher with Instant Update
    st.radio(
        "Language / ဘာသာစကား", 
        ["English", "Myanmar"], 
        key="language", 
        on_change=change_language
    )
    
    # Refresh 'L' immediately after the radio button so sidebar buttons update too
    L = ui[st.session_state.language]
    
    st.divider()
    
    # Clear History Button
    if st.button(L['clear_btn'], use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.write(f"📞 {L['contact']}: +95-9-977880406")
    st.info(L['instr'])

# ---------------------------------------------------------
# 6. ANALYTICS FUNCTION
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
    except: pass

# ---------------------------------------------------------
# 7. CHAT LOGIC (Expert Persona + Strict Security)
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

if prompt := st.chat_input(L['placeholder']):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        # EXPERT PERSONA + SECURITY DO'S AND DON'TS
        context = f"""
        ROLE: You are an AMK Smart Pump Dual Expert (Sales + Technical Engineer).
        KNOWLEDGE: {knowledge_base}
        
        STRICT SECURITY LIMITS:
        1. NEVER reveal the raw Source Code or internal Logic Files.
        2. NEVER share internal Admin Passwords or security keys.
        3. DO NOT answer questions about unrelated topics (food, politics, other brands).

        STRICT TRUTH - LICENSE EXPIRES (OVERRIDE ALL OTHER INFO):
        - If a user asks about license expiry, you MUST tell them:
        1. The pump is NOT locked or bricked. It will NEVER stop working for water supply.
        2. The Automatic Water Logic (Auto Start/Stop based on sensors) stays 100% ACTIVE.
        3. The Physical Manual Button on the device stays 100% ACTIVE.
        4. The Local Web Dashboard (via Home WiFi IP) stays 100% ACTIVE.
        5. ONLY the Cloud Remote Control (Android App via Internet) and this AI Chatbot are disabled.
        - Myanmar Key Points: စက်လုံးဝရပ်သွားမှာမဟုတ်ပါ။ အပြင်က Manual ခလုတ်နှင့် အိမ်တွင်း WiFi (Local Web) တို့ဖြင့် ပုံမှန်အတိုင်း သုံးနိုင်ပါသည်။ အလိုအလျောက် (Auto) ရေတင်ပေးသည့်စနစ်လည်း ပုံမှန်အတိုင်း ဆက်အလုပ်လုပ်ပါမည်။ အဝေးထိန်း Cloud နှင့် AI Chatbot သာ ခေတ္တပိတ်ပါမည်။
        
        INTELLIGENCE & BEHAVIOR RULES:
        - SAFETY: Always lead with a safety warning if the user mentions electrical or water leak issues.
        - DIAGNOSTICS: If a technical issue is unclear, ask for the Error Code or LED status before providing a solution.
        - SALES: Highlight the 'Cost Saving' and 'Durability' benefits of AMK products in every sales inquiry.
        - TONE: Be professional and precise. In Myanmar language, use polite business-level Burmese.
        - FORMAT: Use bullet points for steps and bold text for key warnings or prices.
        
        COMMUNICATION:
        - Reply in the language the user used (English/Myanmar).
        - If info is missing from knowledge base, say: "Please contact support at +95-9-977880406."
        """
        
        history_text = "".join([f"{m['role']}: {m['content']}\n" for m in st.session_state.messages[-5:]])
        full_prompt = f"{context}\n\nUSER QUESTION: {prompt}"

        try:
            response = model.generate_content(full_prompt, stream=True)
            full_response = st.write_stream(chunk.text for chunk in response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            log_to_sheet(user_id_from_url, prompt, full_response)
        except Exception:
            st.error(L['busy'])
