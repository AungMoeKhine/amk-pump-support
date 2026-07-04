import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Model Selection: Using the model available in your list
model = genai.GenerativeModel('gemini-3.5-flash')

# 4. ULTIMATE DARK THEME FIX (Matches cloud_control.html)
st.markdown("""
    <style>
        /* Force transparent background so the HTML app's background shows through */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"], .main {
            background-color: transparent !important;
        }

        /* HIDE ALL STREAMLIT UI ELEMENTS */
        footer {display: none !important;}
        [data-testid="stFooter"] {display: none !important;}
        header {display: none !important;}
        [data-testid="stHeader"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}

        /* FIX MESSAGE DISPLAY: Match HTML App .card style */
        [data-testid="stChatMessage"] {
            background-color: rgba(30, 30, 30, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            padding: 15px !important;
            margin-bottom: 10px !important;
        }
        [data-testid="stChatMessage"] h1, 
        [data-testid="stChatMessage"] h2, 
        [data-testid="stChatMessage"] h3, 
        [data-testid="stChatMessage"] p, 
        [data-testid="stChatMessage"] li,
        [data-testid="stChatMessage"] div {
            color: #FFFFFF !important;
            font-family: sans-serif !important;
        }

        /* FIX INPUT AREA: Match HTML inputs */
        [data-testid="stBottom"] > div {
            background-color: transparent !important;
            padding-bottom: 20px !important;
        }
        
        /* STYLE THE INPUT BOX */
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
            font-family: sans-serif !important;
        }

        /* Title and Padding */
        .block-container { 
            padding-top: 1.5rem !important; 
            padding-bottom: 6rem !important; 
        }
        .main-title {
            font-size: 1.2rem !important; 
            font-weight: 800;
            text-align: center;
            width: 100%;
            color: #FFFFFF !important;
            font-family: sans-serif !important;
            margin-bottom: 2px;
        }
        .sub-caption {
            font-size: 0.75rem !important;
            color: #888888 !important;
            text-align: center;
            width: 100%;
            font-family: sans-serif !important;
            margin-bottom: 15px;
        }

        /* HIDE THE EMBEDDED STREAMLIT FOOTER & BORDER */
        .stApp > header { display: none !important; }
        .stAppViewContainer { background-color: transparent !important; }
        
        /* This targets the "Built with Streamlit" banner */
        #root > div:last-child, 
        .stApp ~ div, 
        [data-testid="stStreamlitFooter"] {
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
