import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK Smart Pump AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Stable Model (1,500 requests/day)
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. TOTAL DARK OVERRIDE (Forces Mobile to match Computer)
st.markdown("""
    <style>
        /* Force total black background on everything */
        html, body, .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stBottom"] {
            background-color: #000000 !important;
            color: #FFFFFF !important;
        }

        /* HIDE ALL WHITE ELEMENTS & FOOTER */
        footer {display: none !important;}
        [data-testid="stFooter"] {display: none !important;}
        header {display: none !important;}
        [data-testid="stHeader"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}

        /* FIX MESSAGE BOXES (White text on dark bubbles) */
        [data-testid="stChatMessage"] {
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
        }
        [data-testid="stChatMessage"] h1, [data-testid="stChatMessage"] h2, 
        [data-testid="stChatMessage"] h3, [data-testid="stChatMessage"] p, 
        [data-testid="stChatMessage"] li, [data-testid="stChatMessage"] div {
            color: #FFFFFF !important;
        }

        /* FIX THE CHAT INPUT (THE YELLOW BOX PROBLEM) */
        /* This forces the container to be black and the box to be grey */
        [data-testid="stBottom"] > div {
            background-color: #000000 !important;
            padding: 10px !important;
        }
        
        [data-testid="stChatInput"] {
            border: 1px solid #444 !important;
            border-radius: 12px !important;
            background-color: #262626 !important; /* Grey Box */
        }
        
        [data-testid="stChatInput"] textarea {
            background-color: #262626 !important; /* Grey Inner Box */
            color: #FFFFFF !important;             /* White Typing Text */
            caret-color: #FFFFFF !important;
        }

        /* Title Spacing and Centering */
        .block-container { 
            padding-top: 2rem !important; 
            padding-bottom: 6rem !important; 
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
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Stable Support Engine (High Quota)</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. CHAT LOGIC
# ---------------------------------------------------------

with open("source_code.cpp", "r") as f:
    knowledge_base = f.read()

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
        context = f"Technical Expert for AMK Pump. Source Code: {knowledge_base}\n\nUser Question: {prompt}"
        try:
            response = model.generate_content(context)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
