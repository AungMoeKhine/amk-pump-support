import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(
    page_title="AMK AI Support", 
    page_icon="💧",
    initial_sidebar_state="expanded" # This forces the sidebar to be open by default
)

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Model Selection (Gemini 3.1 Lite)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

# 4. ULTIMATE DARK THEME & LAYOUT FIX
st.markdown("""
    <style>
        /* Force Deep Grey background */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"], .main {
            background-color: #121212 !important;
            color: #FFFFFF !important;
        }

        /* HIDE DEFAULT HEADER BACKGROUND (Keeps sidebar button visible) */
        header, [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        
        footer, [data-testid="stDecoration"] {
            display: none !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: #1a1a1a !important;
        }

        /* Fix Message Bubbles */
        [data-testid="stChatMessage"] {
            background-color: rgba(30, 30, 30, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
        }
        [data-testid="stChatMessage"] * { color: #FFFFFF !important; }

        /* INPUT BOX ALIGNMENT */
        [data-testid="stBottom"] > div {
            background-color: transparent !important;
            padding: 10px 0px 25px 0px !important;
        }

        [data-testid="stChatInput"] {
            background-color: #262626 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
        }

        /* Header Spacing Fix (Added margin to ensure title shows) */
        .block-container { padding-top: 4rem !important; padding-bottom: 6rem !important; }
        .main-title { font-size: 1.25rem !important; font-weight: 800; text-align: center; width: 100%; color: #FFFFFF !important; }
        .sub-caption { font-size: 0.72rem !important; color: #888888 !important; text-align: center; width: 100%; margin-bottom: 15px; }
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Stable Support Engine • Gemini 3.1 Lite</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. KNOWLEDGE LOADING
# ---------------------------------------------------------
@st.cache_data
def load_knowledge_data():
    try:
        with open("source_code.cpp", "r") as f: code_data = f.read(10000)
        with open("manual.txt", "r") as f: manual_data = f.read()
        return f"TECHNICAL_SPECS:\n{code_data}\n\nTROUBLESHOOTING_MANUAL:\n{manual_data}"
    except Exception:
        return "Knowledge base unavailable."

# --- IMPORTANT: THIS LINE MUST EXIST ---
knowledge_base = load_knowledge_data()

# ---------------------------------------------------------
# SIDEBAR CONTROLS (Updated)
# ---------------------------------------------------------
with st.sidebar:
    # Adding the title back here too
    st.markdown("## 💧 AMK AI Support")
        
    st.divider()
    st.markdown("### 🛠️ Chat Settings")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.markdown("### 📞 Sales Support")
    st.write("Phone: +95-9-977880406")
    st.write("Ask about installation, error codes, pricing, and solving technical issues.")

# ---------------------------------------------------------
# 6. CHAT LOGIC (Complete Analytics Version)
# ---------------------------------------------------------
import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 6.1 LICENSE & USER INFO ---
is_expired_status = st.query_params.get("expired", "False")
user_id = st.query_params.get("id", "Unknown_User") # Capture Cloud ID from URL

if is_expired_status == "True":
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.error("🛑 License Expired / လိုင်စင်သက်တမ်းကုန်ဆုံးနေပါသည်")
    st.info("Please renew your AMK Smart Pump subscription to continue using AI Support.")
    st.warning("ဆက်သွယ်ရန် - +95-9-977880406")
    st.stop() 

# --- 6.2 ANALYTICS FUNCTION ---
def log_to_sheet(question, answer):
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
# --- 6.3 CLEAN CHAT INTERFACE ---
# We use a container to keep the chat history organized
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User Input Box (Always stays at the bottom)
if prompt := st.chat_input("Ask about errors or setup..."):
    # 1. Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Re-render the chat so the user message appears immediately
    st.rerun()

# This handles generating the response IF the last message was from the user
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    last_prompt = st.session_state.messages[-1]["content"]
    
    with st.chat_message("assistant"):
        context = f"ROLE: Senior Support for AMK. KNOWLEDGE: {knowledge_base}"
        # Simplified history for the AI
        history_text = "".join([f"{m['role']}: {m['content']}\n" for m in st.session_state.messages[-6:-1]])
        full_prompt = f"{context}\n\nPAST:\n{history_text}\n\nQUESTION: {last_prompt}"

        try:
            # Generate the response
            response = model.generate_content(full_prompt, stream=True)
            full_response = st.write_stream(chunk.text for chunk in response)
            
            # Save response and log to sheet
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            log_to_sheet(last_prompt, full_response)
            
            # CRITICAL: Rerun one last time to "lock" the message in the history loop
            st.rerun()
            
        except Exception as e:
            st.error("⚠️ System busy. Please try again.")
            st.session_state.messages.pop() # Remove failed prompt
