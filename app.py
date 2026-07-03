import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AMK Smart Pump AI Support", page_icon="💧")

# Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# ---------------------------------------------------------
# AUTO-DETECT CORRECT MODEL (Fixes the 404 Error)
# ---------------------------------------------------------
@st.cache_resource
def get_best_model():
    try:
        # Ask Google which models this specific API key can use
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority list: we want Flash first, then Pro
        if "models/gemini-1.5-flash" in available_models:
            return "models/gemini-1.5-flash"
        elif "models/gemini-1.5-pro" in available_models:
            return "models/gemini-1.5-pro"
        else:
            # If none of those, just use the first one Google offers
            return available_models[0]
    except Exception as e:
        return "models/gemini-1.5-flash" # Default fallback

best_model_name = get_best_model()
model = genai.GenerativeModel(best_model_name)
# ---------------------------------------------------------

# Load the hardware code
with open("source_code.cpp", "r") as f:
    knowledge_base = f.read()

st.title("💧 AMK Smart Pump Support AI")
st.caption(f"Connected via {best_model_name}")

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
        context = f"""
        You are the technical expert for the AMK Smart Pump System. 
        Knowledge Source: {knowledge_base}
        
        Instructions:
        1. Answer based ONLY on the logic in the source code.
        2. Answer in Myanmar language if asked in Myanmar.
        3. Mention hardware pins when helpful.
        """
        
        try:
            # Combine context and prompt
            response = model.generate_content(context + "\n\nUser: " + prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Check your API key or model access in Google AI Studio.")
