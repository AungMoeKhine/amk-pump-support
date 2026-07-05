# 3. GLASSMORPHISM DARK THEME OVERRIDE
st.markdown("""
    <style>
        /* 1. Main Background: Deep Grey with slight transparency */
        .stApp {
            background-color: rgba(18, 18, 18, 0.9) !important;
        }

        /* 2. Hide Streamlit clutter */
        footer, header, [data-testid="stHeader"], [data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* 3. Message Bubbles: Glass effect to match your dashboard */
        [data-testid="stChatMessage"] {
            background-color: rgba(30, 30, 30, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            margin-bottom: 10px !important;
        }
        [data-testid="stChatMessage"] * {
            color: #FFFFFF !important;
        }

        /* 4. Bottom Input Area: Transparent and Centered */
        [data-testid="stBottom"] > div {
            background-color: transparent !important;
            padding-bottom: 20px !important;
        }

        /* 5. The Typing Box: Grey to match your WiFi/PIN inputs */
        [data-testid="stChatInput"] {
            background-color: rgba(42, 42, 42, 0.9) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
        }

        [data-testid="stChatInput"] textarea {
            background-color: transparent !important;
            color: #FFFFFF !important;
            caret-color: #FFFFFF !important;
        }

        /* Spacing and Header */
        .block-container { padding-top: 2rem !important; padding-bottom: 7rem !important; }
        .main-title { font-size: 1.25rem !important; font-weight: 800; text-align: center; width: 100%; color: #FFFFFF !important; }
        .sub-caption { font-size: 0.72rem !important; color: #888888 !important; text-align: center; width: 100%; margin-bottom: 15px; }
    </style>
    <div class="main-title">💧 AMK Smart Pump Support AI</div>
    <div class="sub-caption">Glassmorphism Mode • Gemini 3.5 Frontier</div>
    """, unsafe_allow_html=True)
