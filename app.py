import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Model Selection: Using the model available in your list
model = genai.GenerativeModel('gemini-3.5-flash')

# 4. ULTIMATE DARK THEME FIX (Targets Yellow Boxes)
st.markdown("""
    <style>
        /* Force total black background on everything */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"], .main {
            background-color: #000000 !important;
        }

        /* HIDE ALL STREAMLIT UI ELEMENTS */
        footer {display: none !important;}
        [data-testid="stFooter"] {display: none !important;}
        header {display: none !important;}
        [data-testid="stHeader"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}

        /* FIX MESSAGE DISPLAY: Force White on ALL text levels */
        [data-testid="stChatMessage"] {
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
        }
        [data-testid="stChatMessage"] h1, 
        [data-testid="stChatMessage"] h2, 
        [data-testid="stChatMessage"] h3, 
        [data-testid="stChatMessage"] p, 
        [data-testid="stChatMessage"] li,
        [data-testid="stChatMessage"] div {
            color: #FFFFFF !important;
        }

        /* FIX INPUT AREA: Nuke the White Container */
        [data-testid="stBottom"] > div {
            background-color: #000000 !important;
            padding: 0px !important;
        }
        
        /* STYLE THE INPUT BOX: Dark Grey with White Text */
        [data-testid="stChatInput"] {
            border: 1px solid #444 !important;
            border-radius: 12px !important;
            background-color: #262626 !important;
        }
        [data-testid="stChatInput"] textarea {
            background-color: #262626 !important;
            color: #FFFFFF !important;
            caret-color: #FFFFFF !important;
        }

        /* Title and Padding */
        .block-container { 
            padding-top: 3.5rem !important; 
            padding-bottom: 8rem !important; 
        }
        .main-title {
            font-size: 1.2rem !important; 
            font-weight: 800;
            text-align: center;
            width: 100%;
            color: #FFFFFF !important;
            margin-bottom: 2px;
        }
        .sub-caption {
            font-size: 0.7rem !important;
            color: #888888 !important;
            text-align: center;
            width: 100%;
            margin-bottom: 15px;
        }
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Connected via Gemini 3.5 Frontier (Preview)</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. CHAT LOGIC
# ---------------------------------------------------------

# Load knowledge base once
try:
    with open("source_code.cpp", "r") as f:
        knowledge_base = f.read()
except:
    knowledge_base = "Source code unavailable."

# Initialize session messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about errors or setup..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        # Strict Security Rules
        context = (
            "You are a technical support expert for AMK Smart Pump. "
            "NEVER show actual C++ code lines. If asked for code, explain it is private property. "
            "Help the user by explaining logic or troubleshooting based on this code: "
            + knowledge_base
        )
        
        try:
            # Combine logic
            response = model.generate_content(context + "\n\nUser Question: " + prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"System Error: {str(e)}")
