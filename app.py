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
# Using the model specified in your snippet
model = genai.GenerativeModel('gemini-3.1-flash-lite') 

# ---------------------------------------------------------
# 2. ULTIMATE TRANSPARENCY & BILINGUAL UI STYLES
# ---------------------------------------------------------
st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainViewContainer"], 
        .main, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stBottom"] {
            background-color: transparent !important;
        }

        [data-testid="stChatMessage"] {
            background-color: rgba(30, 30, 30, 0.8) !important;
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .main-title { 
            font-size: 1.4rem !important; 
            font-weight: 800; 
            text-align: center; 
            color: #FFFFFF !important; 
        }
        .sub-caption { 
            font-size: 0.85rem !important; 
            color: #BBBBBB !important; 
            text-align: center; 
            margin-bottom: 15px; 
        }
        /* Support for Myanmar Unicode Font Rendering */
        @import url('https://fonts.googleapis.com/css2?family=Pyidaungsu&display=swap');
        body { font-family: 'Pyidaungsu', sans-serif; }
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">
        Stable Support Engine • Authorized Access Only<br>
        (စမတ်ပန့် အကူအညီပေးရေးစနစ် • တရားဝင်အသုံးပြုခွင့်ရှိသူများသာ)
    </div>
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
# 4. SIDEBAR CONTROLS (Bilingual)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 💧 AMK AI Support")
    st.markdown("*(အေအမ်ကေ အိုင်အေ အကူအညီ)*")
    st.divider()
    
    if st.button("🗑️ Clear Chat History (မှတ်တမ်းဖျက်ရန်)", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.markdown("""
    **Contact / ဆက်သွယ်ရန်:**
    - 📞 Phone: +95-9-977880406
    
    **Instructions / လမ်းညွှန်ချက်:**
    - Ask about installation, error codes, and pricing.
    - တပ်ဆင်ခြင်း၊ အမှားကုဒ်များနှင့် ဈေးနှုန်းများကို မြန်မာလိုဖြစ်စေ၊ အင်္ဂလိပ်လိုဖြစ်စေ မေးမြန်းနိုင်ပါသည်။
    """)

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
# 6. CHAT LOGIC (Bilingual Logic)
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

# Placeholder in both languages
input_placeholder = "Ask about errors or setup... (သိလိုသည်များကို မေးမြန်းပါ...)"
if prompt := st.chat_input(input_placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # UPDATED SYSTEM PROMPT FOR BILINGUAL RESPONSE
        context = f"""
        ROLE: You are a Senior Support Engineer for AMK Smart Pumps.
        KNOWLEDGE: {knowledge_base}
        LANGUAGE RULES: 
        1. If the user asks in Myanmar (Burmese), you MUST respond in Myanmar. 
        2. If the user asks in English, you MUST respond in English.
        3. Use professional, helpful technical tone in both languages.
        4. If technical terms are hard to translate, keep them in English but explain in Myanmar.
        """
        
        history_text = "".join([f"{m['role']}: {m['content']}\n" for m in st.session_state.messages[-6:-1]])
        full_prompt = f"{context}\n\nPAST CONVERSATION:\n{history_text}\n\nUSER QUESTION: {prompt}"

        try:
            response = model.generate_content(full_prompt, stream=True)
            full_response = st.write_stream(chunk.text for chunk in response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            log_to_sheet(user_id_from_url, prompt, full_response)
        except Exception as e:
            st.error("⚠️ System busy. (စနစ် အလုပ်များနေပါသည်။)")
