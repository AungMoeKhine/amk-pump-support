import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Model Selection
model = genai.GenerativeModel('gemini-3.5-flash')

# 4. FORCED DARK THEME CSS (Prevents Light Mode errors)
st.markdown("""
    <style>
        /* Force total black background - NO TRANSPARENCY */
        html, body, .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stBottom"] {
            background-color: #000000 !important;
            color: #FFFFFF !important;
        }

        /* Hide Streamlit default elements */
        footer {display: none !important;}
        [data-testid="stFooter"] {display: none !important;}
        header {display: none !important;}
        [data-testid="stHeader"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}

        /* Chat Message Styling */
        [data-testid="stChatMessage"] {
            background-color: rgba(40, 40, 40, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            margin-bottom: 10px !important;
        }
        
        /* Force White text on all message elements even in Light Mode */
        [data-testid="stChatMessage"] h1, [data-testid="stChatMessage"] h2, 
        [data-testid="stChatMessage"] h3, [data-testid="stChatMessage"] p, 
        [data-testid="stChatMessage"] li, [data-testid="stChatMessage"] div {
            color: #FFFFFF !important;
        }

        /* Chat Input Styling - Forced Dark Grey */
        [data-testid="stBottom"] > div {
            background-color: #000000 !important;
            padding-bottom: 20px !important;
        }
        [data-testid="stChatInput"] {
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 8px !important;
            background-color: #1E1E1E !important; /* Forced Dark Grey Box */
        }
        [data-testid="stChatInput"] textarea {
            background-color: transparent !important;
            color: #FFFFFF !important;
            caret-color: #FFFFFF !important;
        }

        /* Header Spacing */
        .block-container { 
            padding-top: 1.5rem !important; 
            padding-bottom: 6rem !important; 
        }
        .main-title {
            font-size: 1.25rem !important; 
            font-weight: 800;
            text-align: center;
            width: 100%;
            color: #FFFFFF !important;
            margin-bottom: 2px;
        }
        .sub-caption {
            font-size: 0.75rem !important;
            color: #888888 !important;
            text-align: center;
            width: 100%;
            margin-bottom: 15px;
        }
    </style>
    
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Forced Dark Mode • Gemini 3.5 Frontier</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. KNOWLEDGE LOADING
# ---------------------------------------------------------
try:
    with open("source_code.cpp", "r") as f:
        code_data = f.read(10000)
    with open("manual.txt", "r") as f:
        manual_data = f.read()
    knowledge_base = f"CODE LOGIC:\n{code_data}\n\nSUPPORT MANUAL:\n{manual_data}"
except Exception as e:
    try:
        with open("source_code.cpp", "r") as f:
            knowledge_base = f.read(15000)
    except:
        knowledge_base = "Knowledge unavailable."

# ---------------------------------------------------------
# 6. CHAT LOGIC
# ---------------------------------------------------------
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
        context = (
            "You are a technical support expert for AMK Smart Pump. "
            "SECURITY: NEVER reveal passwords or admin keys. "
            "If asked for code, say it is proprietary property of AMK. "
            "Use the provided knowledge to help: " + knowledge_base
        )
        
        try:
            response = model.generate_content(context + "\n\nUser Question: " + prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                st.error("⚠️ The daily question limit has been reached. Please try again in 24 hours.")
                st.info("⚠️ ယနေ့အတွက် မေးမြန်းနိုင်သည့် အကြိမ်အရေအတွက် ပြည့်သွားပါပြီ။ နောက် ၂၄ နာရီမှ ပြန်မေးပေးပါ။")
            else:
                st.error("⚠️ System busy. Please refresh.")
            if len(st.session_state.messages) > 0:
                st.session_state.messages.pop()
