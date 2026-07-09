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
# Using gemini-1.5-flash for better Myanmar language support
model = genai.GenerativeModel('gemini-1.5-flash')

# ---------------------------------------------------------
# 2. ULTIMATE TRANSPARENCY SETUP (Maintained exactly)
# ---------------------------------------------------------
st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainViewContainer"], 
        .main, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stBottom"] {
            background-color: transparent !important;
            background: transparent !important;
        }

        [data-testid="collapsedControl"] {
            background-color: transparent !important;
            background: transparent !important;
            top: 10px;
        }

        [data-testid="stBottom"] > div {
            background-color: transparent !important;
        }

        [data-testid="stChatMessage"] {
            background-color: rgba(30, 30, 30, 0.8) !important;
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .block-container {
            padding-top: 4rem !important;
        }

        [data-testid="stDecoration"] {
            display: none !important;
        }

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
    <div class="sub-caption">Stable Support Engine • Authorized Access Only<br>(စမတ်ပန့် အကူအညီပေးရေးစနစ် • တရားဝင်အသုံးပြုခွင့်ရှိသူများသာ)</div>
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
# 4. SIDEBAR CONTROLS (Bilingual Update)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 💧 AMK AI Support")
    st.divider()
    if st.button("🗑️ Clear Chat / မှတ်တမ်းဖျက်ရန်", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.write("**Contact / ဆက်သွယ်ရန်:**")
    st.write("📞 +95-9-977880406")
    st.info("Ask about installation, error codes, and setup in English or Myanmar.\n\nတပ်ဆင်ခြင်းနှင့် အမှားကုဒ်များကို အင်္ဂလိပ် သို့မဟုတ် မြန်မာဘာသာဖြင့် မေးမြန်းနိုင်ပါသည်။")

# ---------------------------------------------------------
# 5. ANALYTICS FUNCTION (Maintained exactly)
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
# 6. CHAT LOGIC (Bilingual & Security Limits)
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

# Chat input with dual language placeholder
if prompt := st.chat_input("Ask or report errors... (သိလိုသည်များကို မေးမြန်းပါ...)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # UPDATED PERSONA WITH SECURITY LIMITS (DO's & DON'Ts)
        context = f"""
        ROLE: Senior Support Engineer for AMK Smart Pumps.
        KNOWLEDGE BASE: {knowledge_base}
        
        LANGUAGE RULES:
        - If the user speaks Myanmar, respond in clear Myanmar (Unicode).
        - If the user speaks English, respond in English.
        - If mixed, respond in the language that is clearest for technical help.

        SECURITY & BEHAVIOR LIMITS (STRICT):
        1. ONLY answer based on the PROVIDED KNOWLEDGE BASE.
        2. If the answer is not in the manual or code, say "I don't have that specific information. Please contact support at +95-9-977880406."
        3. DO NOT give advice on modifying the pump hardware in a way that violates safety.
        4. DO NOT make up pricing if it is not in the manual.
        5. Stay professional and technical.
        """
        
        history_text = "".join([f"{m['role']}: {m['content']}\n" for m in st.session_state.messages[-6:-1]])
        full_prompt = f"{context}\n\nPAST CONVERSATION:\n{history_text}\n\nUSER QUESTION: {prompt}"

        try:
            response = model.generate_content(full_prompt, stream=True)
            full_response = st.write_stream(chunk.text for chunk in response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            log_to_sheet(user_id_from_url, prompt, full_response)
        except Exception as e:
            st.error("⚠️ System busy / စနစ်ခေတ္တအလုပ်များနေပါသည်။")
