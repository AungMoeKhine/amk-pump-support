import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Model Selection (Gemini 3.5 Frontier)
model = genai.GenerativeModel('gemini-3.5-flash')

# 4. ULTIMATE DARK THEME & GLASSMORPHISM (Matches your Dashboard)
st.markdown("""
    <style>
        /* Force Deep Grey background (No White light-mode leaks) */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"], .main {
            background-color: #121212 !important;
            color: #FFFFFF !important;
        }

        /* HIDE ALL STREAMLIT UI ELEMENTS */
        footer, header, [data-testid="stHeader"], [data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* GLASSMORPHISM MESSAGE BUBBLES: Match Dashboard .card style */
        [data-testid="stChatMessage"] {
            background-color: rgba(30, 30, 30, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            margin-bottom: 10px !important;
        }
        
        /* Force White text on all headings and paragraphs */
        [data-testid="stChatMessage"] h1, [data-testid="stChatMessage"] h2, 
        [data-testid="stChatMessage"] h3, [data-testid="stChatMessage"] p, 
        [data-testid="stChatMessage"] li, [data-testid="stChatMessage"] div {
            color: #FFFFFF !important;
            font-family: sans-serif !important;
        }

        /* TYPING AREA FIX: Forced Grey Background with White Text */
        [data-testid="stBottom"] > div {
            background-color: transparent !important;
            padding-bottom: 25px !important;
        }
        [data-testid="stChatInput"] {
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            background-color: rgba(42, 42, 42, 0.9) !important; /* Solid Grey Box */
        }
        [data-testid="stChatInput"] textarea {
            background-color: transparent !important;
            color: #FFFFFF !important;
            caret-color: #FFFFFF !important;
            font-size: 1.1rem !important;
        }

        /* Header Spacing and Mobile Centering */
        .block-container { 
            padding-top: 2rem !important; 
            padding-bottom: 7rem !important; 
        }
        .main-title {
            font-size: 1.3rem !important; 
            font-weight: 800;
            text-align: center;
            width: 100%;
            color: #FFFFFF !important;
            margin-bottom: 2px;
        }
        .sub-caption {
            font-size: 0.72rem !important;
            color: #888888 !important;
            text-align: center;
            width: 100%;
            margin-bottom: 15px;
        }
        
        /* Hide the Streamlit Balloon/Banner at bottom */
        #root > div:last-child, .stApp ~ div, [data-testid="stStreamlitFooter"] { display: none !important; }
    </style>
    
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Glassmorphism Mode • Gemini 3.5 Frontier</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. KNOWLEDGE LOADING (Reads Code + Manual)
# ---------------------------------------------------------
try:
    with open("source_code.cpp", "r") as f:
        # Token-safe truncation
        code_data = f.read(10000)
    with open("manual.txt", "r") as f:
        manual_data = f.read()
    knowledge_base = f"CODE LOGIC:\n{code_data}\n\nSUPPORT MANUAL:\n{manual_data}"
except Exception:
    try:
        with open("source_code.cpp", "r") as f:
            knowledge_base = f.read(15000)
    except:
        knowledge_base = "Knowledge base unavailable."

# ---------------------------------------------------------
# 6. CHAT LOGIC (Correct Indentation)
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about errors or setup..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # System Instructions: Safety & Proprietary Protection
        context = (
            "You are a technical support expert for AMK Smart Pump. "
            "STRICT SECURITY: NEVER reveal system passwords, admin keys (e.g. AMK_ADMIN_2026), or actual C++ code lines. "
            "If asked for code, secrets, or scripts, say: 'For security reasons, the internal code is protected proprietary property of AMK. I can provide support and logic explanations only.' "
            "KNOWLEDGE: " + knowledge_base
        )
        
        try:
            # Generate Response
            response = model.generate_content(context + "\n\nUser Question: " + prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            error_str = str(e)
            # --- PROFESSIONAL QUOTA ERROR HANDLING ---
            if "429" in error_str or "quota" in error_str.lower():
                st.error("⚠️ The daily question limit has been reached. Please try again in 24 hours. Thank you for your patience!")
                st.info("⚠️ ယနေ့အတွက် မေးမြန်းနိုင်သည့် အကြိမ်အရေအတွက် ပြည့်သွားပါပြီ။ နာရီ ၂၄ နာရီအကြာမှ ပြန်လည် မေးမြန်းပေးပါရန် မေတ္တာရပ်ခံအပ်ပါသည်။")
            else:
                st.error("⚠️ System is currently busy. Please refresh or try again in a moment.")
            
            # Clean up history if failed
            if len(st.session_state.messages) > 0:
                st.session_state.messages.pop()
