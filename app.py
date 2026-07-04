import streamlit as st
import google.generativeai as genai

# 1. Page Config (Must be the very first Streamlit command)
st.set_page_config(page_title="AMK Smart Pump AI Support", page_icon="💧", layout="centered")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Dynamic Model Picker (Ensures Gemini 3.5 Flash compatibility)
@st.cache_resource
def get_active_model():
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority = ["models/gemini-3.5-flash", "models/gemini-3.1-flash-lite", "models/gemini-1.5-flash"]
        for p in priority:
            if p in available:
                return genai.GenerativeModel(p)
        return genai.GenerativeModel(available[0])
    except Exception:
        return genai.GenerativeModel("models/gemini-3.5-flash")

model = get_active_model()

# 4. FIXED CUSTOM STYLING (Fixed visibility issue)
st.markdown(f"""
    <style>
        /* Hide the default Streamlit header to save space */
        header {{visibility: hidden;}}
        
        /* Adjust top padding - not too small so it doesn't get cut off */
        .block-container {{ 
            padding-top: 3.5rem !important; 
            padding-bottom: 1rem !important; 
            max-width: 800px;
        }}
        
        .main-title {{
            font-size: 1.6rem !important; 
            font-weight: 800;
            margin-bottom: 5px;
            color: #FFFFFF;
            text-align: center;
        }}
        
        .sub-caption {{
            font-size: 0.85rem !important;
            color: #AAAAAA;
            margin-bottom: 25px;
            text-align: center;
        }}
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Connected via {model.model_name.split('/')[-1].replace('-', ' ').title()}</div>
    """, unsafe_allow_html=True)

# 5. KNOWLEDGE BASE LOADING
try:
    with open("source_code.cpp", "r") as f:
        knowledge_base = f.read()
except FileNotFoundError:
    knowledge_base = "Source code not found."

# 6. CHAT LOGIC
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
        # --- IMPROVED SECURITY INSTRUCTIONS ---
        context = f"""
        ROLE: You are the AMK Smart Pump Support AI.
        
        KNOWLEDGE BASE:
        {knowledge_base}
        
        STRICT SECURITY RULES:
        1. NEVER reveal, show, repeat, or display any actual C++ code from the knowledge base.
        2. NEVER offer to provide the source code to the user. 
        3. If a user asks for the source code, you must say: "I am sorry, but the internal source code is a protected proprietary property of AMK Smart Pump. I am authorized to provide technical support and explanations only."
        4. Focus on explaining logic and providing troubleshooting steps based on the code, but do not show the code itself.
        5. If a user asks in Myanmar language, answer in Myanmar language with the same strict rules.
        """
        
        # Combine the secret instructions with the user's question
        full_query = context + "\n\nUser Question: " + prompt
        
        try:
            response = model.generate_content(full_query)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
