import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK Smart Pump AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Model Selection (Gemini 3.5 Frontier)
model = genai.GenerativeModel('gemini-3.5-flash')

# 4. COMPLETE UI FIXES (Dark Mode, No Footer, No Cut-off)
st.markdown(f"""
    <style>
        /* Force total black background on everything */
        html, body, .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stBottom"] {{
            background-color: #000000 !important;
            color: #FFFFFF !important;
        }}

        /* HIDE THE WHITE FOOTER BAR COMPLETELY */
        footer {{visibility: hidden !important; height: 0px !important;}}
        [data-testid="stFooter"] {{display: none !important;}}
        [data-testid="stDecoration"] {{display: none !important;}}
        
        /* Fix the Chat Input container (remove white/grey background) */
        [data-testid="stBottom"] > div {{
            background-color: #000000 !important;
            border-top: 1px solid #333 !important;
        }}

        /* Style the Chat Input text box */
        [data-testid="stChatInput"] textarea {{
            background-color: #1A1A1A !important;
            color: #FFFFFF !important;
            border-radius: 10px !important;
        }}

        /* Fix Top Padding to prevent cut-off */
        .block-container {{ 
            padding-top: 4.5rem !important; 
            padding-bottom: 6rem !important; 
        }}

        /* Header Styling (Small, Centered, White) */
        .main-title {{
            font-size: 1.2rem !important; 
            font-weight: 800;
            text-align: center;
            width: 100%;
            color: #FFFFFF !important;
            margin-bottom: 2px;
        }}
        .sub-caption {{
            font-size: 0.7rem !important;
            color: #888888 !important;
            text-align: center;
            width: 100%;
            margin-bottom: 15px;
        }}
        
        /* Make chat bubbles darker to match */
        [data-testid="stChatMessage"] {{
            background-color: #111111 !important;
            border: 1px solid #222 !important;
            border-radius: 15px !important;
        }}
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Connected via Gemini 3.5 Frontier (Preview Quota)</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. CHAT LOGIC
# ---------------------------------------------------------

# Load the hardware code knowledge
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
        # The System Instruction + User Prompt
        context = f"Technical Expert for AMK Pump. Source Code: {knowledge_base}\n\nUser: {prompt}"
        try:
            response = model.generate_content(context)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"System Error: {str(e)}")
