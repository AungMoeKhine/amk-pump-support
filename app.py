import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Model Selection (Gemini 3.1 Lite)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

# 4. ULTIMATE DARK THEME & LAYOUT FIX
st.markdown("""
    <style>
        /* Force Deep Grey background */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"], .main {
            background-color: #121212 !important;
            color: #FFFFFF !important;
        }

        /* Hide Clutter */
        footer, header, [data-testid="stHeader"], [data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Fix Message Bubbles */
        [data-testid="stChatMessage"] {
            background-color: rgba(30, 30, 30, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
        }
        [data-testid="stChatMessage"] * { color: #FFFFFF !important; }

        /* FIX INPUT BOX ALIGNMENT (Prevents button from jumping to next line) */
        [data-testid="stBottom"] > div {
            background-color: transparent !important;
            padding: 10px 0px 25px 0px !important;
        }

        [data-testid="stChatInput"] {
            background-color: #262626 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            display: flex !important;
            flex-direction: row !important; 
            flex-wrap: nowrap !important; /* <--- THIS FORCES THE BUTTON TO STAY RIGHT */
            align-items: center !important;
        }

        [data-testid="stChatInput"] textarea {
            background-color: transparent !important;
            color: #FFFFFF !important;
            font-size: 0.95rem !important;
        }

        /* Header Spacing */
        .block-container { padding-top: 1.5rem !important; padding-bottom: 6rem !important; }
        .main-title { font-size: 1.25rem !important; font-weight: 800; text-align: center; width: 100%; color: #FFFFFF !important; }
        .sub-caption { font-size: 0.72rem !important; color: #888888 !important; text-align: center; width: 100%; margin-bottom: 15px; }
        #root > div:last-child, .stApp ~ div, [data-testid="stStreamlitFooter"] { display: none !important; }
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Stable Support Engine • Gemini 3.1 Lite</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. KNOWLEDGE LOADING (Clean & Matched Labels)
# ---------------------------------------------------------
try:
    with open("source_code.cpp", "r") as f:
        code_data = f.read(10000)
    with open("manual.txt", "r") as f:
        manual_data = f.read()
    # These labels MUST match the Instructions in Part 6
    knowledge_base = f"TECHNICAL_SPECS:\n{code_data}\n\nTROUBLESHOOTING_MANUAL:\n{manual_data}"
except Exception:
    knowledge_base = "Knowledge base currently unavailable."

# ---------------------------------------------------------
# 6. CHAT LOGIC (Complete Optimized Block)
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history on the screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Box
if prompt := st.chat_input("Ask about errors or setup..."):
    # 1. Add user message to history and show it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Assistant Response
    with st.chat_message("assistant"):
        # Define the AI's instructions
        context = f"""
        ROLE: Senior Customer Support & Sales for AMK Smart Automation.
        KNOWLEDGE SOURCE: {knowledge_base}
        STRICT RULES:
        1. NO SECRETS: Never reveal passwords/keys.
        2. NO JARGON: Use simple terms (e.g., 'Cloud Connection' not 'MQTT').
        3. SIMPLE MYANMAR: Use easy-to-understand Myanmar language.
        4. SALES: Provide +95-9-977880406 for pricing/shop info.
        5. SECURITY: Never show C++ code or technical function names.
        """
        
        # Build the conversation history (Last 5 messages, excluding the current one)
        history_text = ""
        for msg in st.session_state.messages[-6:-1]:
            role = "Customer" if msg["role"] == "user" else "AI Support"
            history_text += f"{role}: {msg['content']}\n"

        full_prompt = f"{context}\n\nPAST CONVERSATION:\n{history_text}\n\nNEW QUESTION: {prompt}"

        try:
            # Generate response with Streaming (Typewriter effect)
            response = model.generate_content(full_prompt, stream=True)
            
            # Display text as it arrives
            full_response = st.write_stream(chunk.text for chunk in response)
            
            # Save the final full response to memory
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                st.error("⚠️ Daily limit reached. Please try again in 24 hours.")
                st.info("⚠️ ယနေ့အတွက် မေးမြန်းနိုင်သည့် အကြိမ်အရေအတွက် ပြည့်သွားပါပြီ။")
            else:
                st.error("⚠️ System busy. Please refresh the page.")
            
            # Remove the last user message if AI failed to answer
            if len(st.session_state.messages) > 0:
                st.session_state.messages.pop()
                
