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
# 2. DARK THEME (Original UI Restored)
# ---------------------------------------------------------
st.markdown("""
    <style>
        /* Keep only the background colors */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"], .main {
            background-color: #121212 !important;
            color: #FFFFFF !important;
        }

        [data-testid="stSidebar"] { background-color: #1a1a1a !important; }
        
        [data-testid="stChatMessage"] {
            background-color: rgba(30, 30, 30, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
        }
        
        [data-testid="stChatMessage"] * { color: #FFFFFF !important; }
        
        [data-testid="stBottom"] > div { background-color: transparent !important; padding-bottom: 25px !important; }
        [data-testid="stChatInput"] { background-color: #262626 !important; border-radius: 10px !important; }
        
        .block-container { padding-top: 4rem !important; padding-bottom: 6rem !important; }
        
        .main-title { font-size: 1.25rem !important; font-weight: 800; text-align: center; width: 100%; color: #FFFFFF !important; margin-top: 10px;}
        .sub-caption { font-size: 0.72rem !important; color: #888888 !important; text-align: center; width: 100%; margin-bottom: 15px; }
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Stable Support Engine • Gemini 3.1 Lite</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. KNOWLEDGE LOADING (Cached for Speed)
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
# 4. SIDEBAR CONTROLS
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
# 5. ANALYTICS FUNCTION (Google Sheets)
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

# --- 6.1 URL PARAMETER SYNC ---
is_expired_status = st.query_params.get("expired", "False")
user_id_from_url = st.query_params.get("id", "Unknown_User")

# --- 6.2 LICENSE LOCK ---
if is_expired_status == "True":
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.error("🛑 License Expired / လိုင်စင်သက်တမ်းကုန်ဆုံးနေပါသည်")
    st.info("Please renew your AMK Smart Pump subscription to continue using AI Support.")
    st.stop() 

# --- 6.3 CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Message History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about errors or setup..."):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        # --- THE SECURITY GUARD ---
        context = f"""
        ROLE: Senior Customer Support & Sales for AMK Smart Automation.
        KNOWLEDGE SOURCE: {knowledge_base}
        
        STRICT COMMUNICATION RULES:
        1. NO SECRETS: NEVER mention passwords like 'AMK_ADMIN_2026' or 'ACER123'. Say they are for authorized technicians only.
        2. NO JARGON: Use simple terms like 'Cloud Connection' (not MQTT) and 'Secure System' (not TLS).
        3. SIMPLE MYANMAR: Always use easy-to-understand Myanmar language. 
        4. SALES: Always provide +95-9-977880406 for pricing.
        5. SECURITY: NEVER show lines of C++ code or technical function names.
        """
        
        # History Context (Past 5 messages)
        history_text = "".join([f"{m['role']}: {m['content']}\n" for m in st.session_state.messages[-6:-1]])
        full_prompt = f"{context}\n\nPAST CONVERSATION:\n{history_text}\n\nUSER QUESTION: {prompt}"

        try:
            # Typewriter Effect Generation
            response = model.generate_content(full_prompt, stream=True)
            full_response = st.write_stream(chunk.text for chunk in response)
            
            # Save to Memory
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Log to Google Sheets
            log_to_sheet(user_id_from_url, prompt, full_response)
            
        except Exception as e:
            st.error("⚠️ System busy. Please try again.")
            if len(st.session_state.messages) > 0:
                st.session_state.messages.pop()
                
