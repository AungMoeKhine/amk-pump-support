import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Model Selection: Gemini 3.1 Flash Lite (High Performance)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

# 4. ULTIMATE DARK THEME & LAYOUT FIX
st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"], .main {
            background-color: #121212 !important;
            color: #FFFFFF !important;
        }
        footer, header, [data-testid="stHeader"], [data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
        }
        [data-testid="stChatMessage"] {
            background-color: rgba(30, 30, 30, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            margin-bottom: 10px !important;
        }
        [data-testid="stChatMessage"] * { color: #FFFFFF !important; }
        [data-testid="stBottom"] > div { background-color: transparent !important; padding: 10px 0px 25px 0px !important; }
        [data-testid="stChatInput"] {
            background-color: #262626 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
        }
        [data-testid="stChatInput"] textarea { background-color: transparent !important; color: #FFFFFF !important; font-size: 0.95rem !important; }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 6rem !important; }
        .main-title { font-size: 1.25rem !important; font-weight: 800; text-align: center; width: 100%; color: #FFFFFF !important; margin-bottom: 2px; }
        .sub-caption { font-size: 0.72rem !important; color: #888888 !important; text-align: center; width: 100%; margin-bottom: 15px; }
        #root > div:last-child, .stApp ~ div, [data-testid="stStreamlitFooter"] { display: none !important; }
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Stable Support Engine • Gemini 3.1 Lite</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. KNOWLEDGE LOADING
# ---------------------------------------------------------
try:
    with open("source_code.cpp", "r") as f:
        code_data = f.read(10000)
    with open("manual.txt", "r") as f:
        manual_data = f.read()
    knowledge_base = f"TECHNICAL_SPECS:\n{code_data}\n\nTROUBLESHOOTING_MANUAL:\n{manual_data}"
except Exception:
    knowledge_base = "Knowledge base unavailable."

# ---------------------------------------------------------
# 6. CHAT LOGIC
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about logic, errors, or setup..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # UPDATED SYSTEM INSTRUCTIONS
        context = f"""
        ROLE: Senior IoT Support Engineer for AMK Smart Automation.
        
        INSTRUCTIONS:
        1. Answer in the same language as the user (Myanmar or English).
        2. For troubleshooting, prioritize the 'TROUBLESHOOTING_MANUAL' text.
        3. For 'how it works' or specs, use the 'TECHNICAL_SPECS' text.
        4. If the user mentions a hardware failure or broken component, suggest calling Aung Moe Khine at +95-9-977880406.
        5. SECURITY: NEVER reveal passwords, secret keys (AMK_ADMIN_2026), or actual C++ code lines.
        
        KNOWLEDGE BASE:
        {knowledge_base}
        """
        
        try:
            response = model.generate_content(context + "\n\nUser Question: " + prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                st.error("⚠️ The daily question limit has been reached. Please try again in 24 hours. Thank you for your patience!")
                st.info("⚠️ ယနေ့အတွက် မေးမြန်းနိုင်သည့် အကြိမ်အရေအတွက် ပြည့်သွားပါပြီ။ နာရီ ၂၄ နာရီအကြာမှ ပြန်လည် မေးမြန်းပေးပါရန် မေတ္တာရပ်ခံအပ်ပါသည်။")
            else:
                st.error("⚠️ System is currently busy. Please refresh or try again in a moment.")
            if len(st.session_state.messages) > 0:
                st.session_state.messages.pop()
