import streamlit as st
import google.generativeai as genai
import paho.mqtt.client as mqtt
import json

# 1. Page Config
st.set_page_config(page_title="AMK AI Support", page_icon="💧")

# 2. Setup AI 
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# ---------------------------------------------------------
# 3. BACKGROUND MQTT LISTENER (The "Silent Ear")
# ---------------------------------------------------------
if 'device_data' not in st.session_state:
    st.session_state.device_data = "Waiting for live data sync..."

def on_message(client, userdata, message):
    try:
        # Decode the JSON status sent by your ESP32
        payload = json.loads(message.payload.decode("utf-8"))
        # We store the 'info', 'vStat', and 'logs' from your ESP32 JSON
        st.session_state.device_data = f"Status: {payload.get('info')}\nLogs: {payload.get('logs')}"
    except:
        pass

@st.cache_resource
def start_mqtt_listener():
    # Use the same credentials as your dashboard
    client = mqtt.Client()
    client.username_pw_set("Smart_Pump", "Sm@rt_Pump_2026")
    client.on_message = on_message
    client.tls_set() # Enable SSL
    client.connect("210195b635414206adcd944325fe6f59.s1.eu.hivemq.cloud", 8883)
    # Replace the ID below with your actual Device ID or a wildcard
    client.subscribe("smartpump/+/status") 
    client.loop_start()
    return client

mqtt_client = start_mqtt_listener()

# ---------------------------------------------------------
# 4. CUSTOM CSS (Glassmorphism)
# ---------------------------------------------------------
st.markdown("""
    <style>
        .stApp { background-color: #121212 !important; }
        footer, header, [data-testid="stHeader"] { display: none !important; }
        [data-testid="stChatMessage"] {
            background-color: rgba(30, 30, 30, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
        }
        [data-testid="stChatMessage"] * { color: #FFFFFF !important; }
        .block-container { padding-top: 2rem !important; }
        .main-title { font-size: 1.3rem !important; font-weight: 800; text-align: center; color: #FFFFFF; }
        #root > div:last-child { display: none !important; }
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div style="text-align:center; font-size:0.7rem; color:#888;">Background Sync Active (Live)</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. KNOWLEDGE LOADING
# ---------------------------------------------------------
try:
    with open("source_code.cpp", "r") as f:
        code_data = f.read(10000)
    with open("manual.txt", "r") as f:
        manual_data = f.read()
except:
    code_data = "Logic hidden."
    manual_data = "Manual offline."

# ---------------------------------------------------------
# 6. CHAT LOGIC
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Combine Manual + Source Code + LIVE DATA FROM MQTT
        knowledge_base = f"CODE:\n{code_data}\n\nMANUAL:\n{manual_data}\n\nLIVE_DEVICE_STATE:\n{st.session_state.device_data}"
        
        context = "Technical Expert for AMK Pump. Rules: No code sharing. KNOWLEDGE: " + knowledge_base
        
        try:
            response = model.generate_content(context + "\n\nUser: " + prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("Limit reached or System Busy.")
