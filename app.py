import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Model Selection (Gemini 3.5 Frontier)
model = genai.GenerativeModel('gemini-3.5-flash')

# 4. CUSTOM CSS: Glassmorphism, Dark Theme, and UI Cleanup
st.markdown("""
    <style>
        /* Force transparency so the dashboard background shows through */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"], .main {
            background-color: transparent !important;
        }

        /* Hide Streamlit default elements */
        footer {display: none !important;}
        [data-testid="stFooter"] {display: none !important;}
        header {display: none !important;}
        [data-testid="stHeader"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}

        /* Chat Message Styling (Glassmorphism) */
        [data-testid="stChatMessage"] {
            background-color: rgba(30, 30, 30, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            margin-bottom: 10px !important;
        }
        
        /* Force White text on all message elements */
        [data-testid="stChatMessage"] h1, [data-testid="stChatMessage"] h2, 
        [data-testid="stChatMessage"] h3, [data-testid="stChatMessage"] p, 
        [data-testid="stChatMessage"] li, [data-testid="stChatMessage"] div {
            color: #FFFFFF !important;
            font-family: sans-serif !important;
        }

        /* Chat Input Styling */
        [data-testid="stBottom"] > div {
            background-color: transparent !important;
            padding-bottom: 20px !important;
        }
        [data-testid="stChatInput"] {
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
            background-color: rgba(42, 42, 42, 0.8) !important;
        }
        [data-testid="stChatInput"] textarea {
            background-color: transparent !important;
            color: #FFFFFF !important;
            caret-color: #FFFFFF !important;
            font-size: 1.1rem !important;
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

        /* Hide the "Built with Streamlit" banner specifically */
        #root > div:last-child, .stApp ~ div, [data-testid="stStreamlitFooter"] {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
        }
    </style>
    
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Connected via Gemini 3.5 Frontier (Preview)</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. CHAT LOGIC
# ---------------------------------------------------------

# Load knowledge base (Truncated for performance)
try:
    with open("source_code.cpp", "r") as f:
        knowledge_base = f.read(15000) 
        knowledge_base += "\n\n...[CODE TRUNCATED]..."
except:
    knowledge_base = "Source code unavailable."

# Initialize history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process input
if prompt := st.chat_input("Ask about errors or setup..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # System Instructions
        context = (
            "You are a technical support expert for AMK Smart Pump. "
            "SECURITY RULES: NEVER reveal system passwords, admin keys (e.g. AMK_ADMIN_2026), or C++ code lines. "
            "If asked for code or secrets, state: 'For security reasons, I cannot provide admin passwords or secret keys. Please contact official AMK technical support.' "
            "Use logic from this code to troubleshoot: " + knowledge_base
        )
        
        try:
            # Generate AI response
            response = model.generate_content(context + "\n\nUser Question: " + prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            error_str = str(e)
            # --- CUSTOM ERROR HANDLING ---
            if "429" in error_str or "quota" in error_str.lower():
                st.error("⚠️ The daily question limit has been reached. Please try again in 24 hours. Thank you for your patience!")
                st.info("⚠️ ယနေ့အတွက် မေးမြန်းနိုင်သည့် အကြိမ်အရေအတွက် ပြည့်သွားပါပြီ။ နာရီ ၂၄ နာရီအကြာမှ ပြန်လည် မေးမြန်းပေးပါရန် မေတ္တာရပ်ခံအပ်ပါသည်။")
            else:
                st.error("⚠️ System is currently busy. Please refresh or try again in a moment.")
            
            # Clean up history if failed
            if len(st.session_state.messages) > 0:
                st.session_state.messages.pop()
