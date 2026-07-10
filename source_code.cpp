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
 * - LICENSING: Token verified via MD5(MAC+Expiry). Disables cloud control parts only if expired, and still able to use directly from device or via local web control page.
 * - DND MODE: NTP-based schedule prevents night auto-starts.
