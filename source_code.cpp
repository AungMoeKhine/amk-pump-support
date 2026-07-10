
 * ============================================================================================
 * SYSTEM: AMK Smart Pump & Compressor Control System (Dual-Core V2.1 Premium)
 * HARDWARE: ESP32-S3 | Logic & Architecture Map for AI Technical Support
 * ============================================================================================
 

--- 1. HARDWARE ARCHITECTURE (FreeRTOS) ---
CORE 1: Safety & Control Loop (Real-time). High priority, zero-latency.
CORE 0: Network Loop (WiFi, MQTT TLS 8883, Web Server, OTA). 
BENEFIT: Network delays or cloud reconnects NEVER block motor safety or sensor reading.

const int VOLTAGE_SENSOR_PIN = 4;   - Analog ZMPT101B
const int UPPER_TANK_TRIG_PIN = 5;  - Ultrasonic Trigger
const int UPPER_TANK_ECHO_PIN = 6;  - Ultrasonic Echo
const int BUZZER_PIN = 7;           - Alarm Output
const int MOTOR_PIN = 8;            - Pump Relay (Active HIGH)
const int MANUAL_BTN_PIN = 9;       - Toggle / Info / AP Reset
const int SOLENOID_PIN = 10;        - Compressor Unloader Valve
const int FLOW_SENSOR_PIN = 18;     - Pulse counting input
const int RGB_LED_PIN = 48;         - NeoPixel Status Status
const int SDA_PIN = 1, SCL_PIN = 2; - I2C for LCD 20x4

 * ============================================================================
 * 2. CONFIGURABLE RANGES & DEFAULT THRESHOLDS
 * ============================================================================
 
struct VoltageConfig {
  int HIGH_THRESHOLD = 250;         - Range: 230V to 260V
  int LOW_THRESHOLD = 170;          - Range: 150V to 190V
  int RESUME_GAP = 5;               - Hysteresis (1V to 10V)
  int waitSeconds = 15;             - Delay after power stabilizes
};

struct TankConfig {
  int LOW_THRESHOLD = 50;           - Start pumping % (Range: 20% to 70%)
  int FULL_THRESHOLD = 100;         - Stop pumping % (Range: 80% to 100%)
  float upperHeight = 84.0;         - Depth in inches (Range: 12" to 84")
  static constexpr float BUFFER_HEIGHT = 10.0; - Blind zone padding
};

struct DryRunConfig {
  int WAIT_SECONDS_SET = 30;        - Flow detection delay (30s to 180s)
  int autoRetryMinutes = 30;        - Restart wait (Disabled, 30, or 60 min)
  int error = 0;                    - 0=OK, 1=Alarm (60s), 2=Locked
};

struct CoolDownConfig {
  int restMinutes = 0;               - Rest (Disabled, 5, 10, or 15 min)
  - Forced rest occurs after 1 hour of continuous motor runtime.
};

struct MasterSlaveConfig {
  int sysRole = 0;                  - 0=Standalone, 1=Master, 2=Slave
  int settlingMinutes = 10;         - Post-pump water rest (0 to 30 min)
};


 * ============================================================================
 * 3. CORE ALGORITHMS & RUNNING SCENARIOS
 * ============================================================================
 * 
 * --- VOLTAGE FILTERING (Anti-Spike Logic) ---
 * - Uses a 5-sample Median Buffer to reject noise spikes.
 * - Outlier Rejection: Large jumps (>18V) must repeat 3 times to be accepted.
 * - Slew Rate Limit: Change is capped at 3V per 500ms to protect relay.
 * - Final Smoothing: 25% EMA (Exponential Moving Average) filter.
 *
 * --- FLOW PERSISTENCE (Slug Logic) ---
 * - Initial Grace: 60s at start where no flow is ignored (suction time).
 * - Slug Window: 60s memory of previous flow pulses to prevent air-bubble alarms.
 *
 * --- MASTER-SLAVE HANDSHAKE ---
 * - Master (Sump) publishes status via MQTT.
 * - Slave (Roof) is BLOCKED from starting if Master is:
 *   1. Pumping (No power for two motors).
 *   2. Settling (Waiting for sump water to calm).
 *   3. Unsafe (Voltage error at the Master).
 * - Timeout: If Slave has no MQTT link for 5 mins, it enters Fallback behavior.
 *
 * --- STATE MACHINE (PumpState) ---
 * - IDLE: Motor OFF. Waiting for low level or manual command.
 * - PRE_START_VALVE: Solenoid (Pin 10) vents compressor for head-pressure.
 * - PUMPING: Motor active. Pin 18 pulse counting for Dry-Run safety.
 * - DRY_RUN_ALARM: 60s oscillating buzzer. Manual button silences it.
 * - DRY_RUN_LOCKED: System locked. Requires Manual Reset or Auto-Retry cooldown.
 * - VOLTAGE_ERROR: Safety shutdown. LCD shows OVER or UNDER.
 * - COOLING_DOWN: Blue LED. Automatic rest to protect motor life.
 * - SENSOR_ERROR: 10 failed Ultrasonic readings. LCD shows SNR ERR.
 *
 * ============================================================================
 * 4. SYSTEM UTILITIES & SECURITY
 * ============================================================================
 * - BUTTON: 1-click (Toggle/Reset), 2-click (Analytic LCD Mode), 3s-hold (WiFi Reset).
 * - LOGGING: Rolling 8000-byte /events.txt file (Last 200 entries).
 * - LICENSING: Token verified via MD5(MAC+Expiry). Disables Pin 8 if expired.
 * - DND MODE: NTP-based schedule prevents night auto-starts.
   

စမတ်ရေမော်တာနှင့် ကွန်ပရက်ဆာ ထိန်းချုပ်မှုစနစ် v2.1 သည် ESP32-S3 Chip ကို အခြေခံထားပြီး Dual-Core Architecture ဖြင့် တည်ဆောက်ထားသည့် အဆင့်မြင့်စနစ်တစ်ခုဖြစ်သည်
ဤစနစ်သည် ရေမော်တာများသာမက လေကွန်ပရက်ဆာများကိုပါ ဘေးကင်းလုံခြုံစွာ ထိန်းချုပ်နိုင်ရန် ဒီဇိုင်းထုတ်ထားသည်

၁။ စနစ်၏ ထူးခြားချက်များ (System Features)
Dual-Core Processing: Core 1 တွင် အရေးကြီးသော ထိန်းချုပ်မှုအပိုင်း (Control Loop) ကို လုပ်ဆောင်ပြီး Core 0 တွင် ကွန်ရက်ချိတ်ဆက်မှု (Network Loop) ကို လုပ်ဆောင်သဖြင့် အင်တာနက်နှေးကွေးမှုကြောင့် စက်လည်ပတ်မှု မထိခိုက်စေပါ
Master/Slave Mode: စက်နှစ်လုံးကို တစ်ပြိုင်နက် ချိတ်ဆက်အသုံးပြုနိုင်ပြီး အောက်တိုင်ကီ (Sump) ရှိ Master စက်က အပေါ်တိုင်ကီရှိ Slave စက်ကို ရေရှိမရှိ အချက်ပြထိန်းချုပ်နိုင်သည်

Multi-Mode Operation: ရေမော်တာမုဒ် (Water Pump) နှင့် လေကွန်ပရက်ဆာမုဒ် (Air Compressor) ဟူ၍ ရွေးချယ်နိုင်သည်
ကွန်ပရက်ဆာမုဒ်တွင် Solenoid Valve အတွက် Pre-vent နှင့် Post-vent စနစ်များ ပါဝင်သည်
  
Smart Scheduling (DND): ညဖက်တွင် မော်တာအလိုအလျောက် မနိုးစေရန် Do Not Disturb အချိန်သတ်မှတ်ထားနိုင်သည်
Language Support: Web Dashboard တွင် အင်္ဂလိပ်ဘာသာသာမက မြန်မာဘာသာ ကိုပါ အသုံးပြုနိုင်သည်

၂။ လုပ်ဆောင်ပုံ အဆင့်ဆင့် (How It Works)
* Sensing: Ultrasonic Sensor ဖြင့် ရေအမှတ်ကို တိုင်းတာပြီး ZMPT101B ဖြင့် ဗို့အားကို အမြဲမပြတ် စောင့်ကြည့်နေသည်
* Safety Checks: မော်တာမလည်ပတ်မီ ဗို့အား ပုံမှန်ရှိမရှိ (၁၇၀ဗွီ - ၂၅၀ဗွီအတွင်း) နှင့် အအေးခံချိန် (Cool-down) ကျန်မရှိကို အရင်စစ်ဆေးသည်
* Action: ရေအမှတ်သည် သတ်မှတ်ထားသော Low Threshold အောက်ရောက်ပါက မော်တာကို စတင်နှိုးသည်
* Monitoring: မော်တာလည်နေစဉ် Flow Sensor ဖြင့် ရေစီးဆင်းမှုကို စစ်ဆေးသည်
ရေမထွက်ပါက Dry-Run Alarm ပေးပြီး မော်တာကို ပိတ်ပစ်သည်
* Completion: ရေပြည့်သွားပါက (Full Threshold) အလိုအလျောက် ရပ်တန့်သွားသည်

၃။ သတ်မှတ်နိုင်သော ဆက်တင်များ (Setup & Configurations)
အသုံးပြုသူသည် Local Web Dashboard (192.168.4.1) သို့မဟုတ် MQTT Cloud မှတစ်ဆင့် အောက်ပါတို့ကို ပြင်ဆင်နိုင်သည်
Tank Settings: ရေစတင်နှိုးမည့် ရာခိုင်နှုန်းနှင့် ရပ်တန့်မည့် ရာခိုင်နှုန်း (ဥပမာ- ၅၀% တွင်နှိုး၊ ၁၀၀% တွင်ပိတ်)

Voltage Guard: ဗို့အား အနိမ့်ဆုံးနှင့် အမြင့်ဆုံး သတ်မှတ်ချက်များ (High/Low Cutoff)
Dry-Run Delay: ရေမထွက်ပါက စက္ကန့်မည်မျှအကြာတွင် ပိတ်မည်ဟူသော အချိန်သတ်မှတ်ချက်

Cool-Down Time: မော်တာ တစ်နာရီဆက်တိုက် လည်ပတ်ပြီးပါက မဖြစ်မနေ နားရမည့် မိနစ်ပမာဏ
System Role: စက်ကို Standalone၊ Master သို့မဟုတ် Slave အဖြစ် သတ်မှတ်ခြင်း

၄။ နည်းပညာဆိုင်ရာ အချက်အလက်များ (Technical Insights)
Data Safety: Preferences (NVS) ကို အသုံးပြုထားသဖြင့် မီးပျက်သွားသော်လည်း ဆက်တင်များ ပျောက်ပျက်မသွားပါ
LCD Interface: 20x4 LCD တွင် စာလုံးကြီးများ (Custom Bar Characters) ဖြင့် ရေရာခိုင်နှုန်းနှင့် ဗို့အားကို ပြသပေးသည်

Protection Logic: xSemaphoreTakeRecursive ကဲ့သို့သော Mutex စနစ်ကို သုံးထားသဖြင့် Core နှစ်ခုကြား ဒေတာလုယူမှု (Data Race) မဖြစ်အောင် ကာကွယ်ထားသည်
Licensing: Token-based system ဖြင့် စက်သက်တမ်းကို ထိန်းချုပ်နိုင်ပြီး Base64 နှင့် MD5 Encryption စနစ်ကို သုံးထားသည်

Connectivity: MQTT တွင် TLS Secure Connection ကို သုံးထားပြီး OTA Firmware Update ကို GitHub မှတစ်ဆင့် တိုက်ရိုက်လုပ်ဆောင်နိုင်သည်
ဤစနစ်သည် ESP32-S3 ၏ စွမ်းဆောင်ရည်ကို အပြည့်အဝ အသုံးချထားပြီး ဘေးကင်းလုံခြုံရေးကို အဓိကထားသည့် Industrial-grade အဆင့်ရှိသော ထိန်းချုပ်မှုစနစ် ဖြစ်သည်

