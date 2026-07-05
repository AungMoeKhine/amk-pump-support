import streamlit as st
import google.generativeai as genai
import paho.mqtt.client as mqtt  # NEW
import json                      # NEW

import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="AMK AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# ---------------------------------------------------------
# NEW: SILENT BACKGROUND SYNC (MQTT)
# ---------------------------------------------------------
if 'live_logs' not in st.session_state:
    st.session_state.live_logs = "Waiting for live data sync..."

def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        # Extracts only the logs and info strings from your ESP32 status JSON
        st.session_state.live_logs = f"Status: {payload.get('info')}\nLogs: {payload.get('logs')}"
    except:
        pass

@st.cache_resource
def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set("Smart_Pump", "Sm@rt_Pump_2026")
    client.on_message = on_message
    client.tls_set() # Required for HiveMQ Port 8883
    client.connect("210195b635414206adcd944325fe6f59.s1.eu.hivemq.cloud", 8883)
    client.subscribe("smartpump/+/status") # Listens to all your devices
    client.loop_start()
    return client

mqtt_client = start_mqtt()

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
# 5. KNOWLEDGE LOADING (Silent Background Version)
# ---------------------------------------------------------
try:
    with open("source_code.cpp", "r") as f:
        code_data = f.read(10000)
    with open("manual.txt", "r") as f:
        manual_data = f.read()
except:
    code_data = "Logic hidden."
    manual_data = "Manual offline."

# C. Combine everything into one "Brain"
# We now use st.session_state.live_logs which updates silently
knowledge_base = f"""
TECHNICAL_SPECS:
{code_data}

TROUBLESHOOTING_MANUAL:
{manual_data}

CURRENT_LIVE_SYSTEM_LOGS (SYNCED IN BACKGROUND):
{st.session_state.live_logs}
"""

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
        # UPDATED SYSTEM INSTRUCTIONS (More professional & helpful)
        context = f"""
        ROLE: Senior IoT Support Engineer for AMK Smart Automation.
        
        INSTRUCTIONS:
        1. Answer in the same language as the user (Myanmar or English).
        2. For troubleshooting, prioritize the 'TROUBLESHOOTING_MANUAL' text.
        3. For 'how it works' or specs, use the 'TECHNICAL_SPECS' text.
        4. If the user mentions a hardware failure or broken component, suggest calling Aung Moe Khine at +95-9-977880406.
        5. SECURITY: NEVER reveal passwords, secret keys (AMK_ADMIN_2026), or actual C++ code lines.
        
        KNOWLEDGE BASE:
        {knowledge_base}
        """        
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
