/* 
 * SYSTEM: AMK Smart Pump & Compressor Control (Dual-Core)
 * VERSION: 2.1 (Premium) | HARDWARE: ESP32-S3
 * LOGIC SUMMARY FOR AI SUPPORT:
 */

// --- PINOUT CONFIGURATION ---
const int SDA_PIN = 1, SCL_PIN = 2;
const int VOLTAGE_SENSOR_PIN = 4;   // ZMPT101B
const int UPPER_TANK_TRIG_PIN = 5;  // Ultrasonic Trig
const int UPPER_TANK_ECHO_PIN = 6;  // Ultrasonic Echo
const int BUZZER_PIN = 7;           // Alarm Output
const int MOTOR_PIN = 8;            // Pump Relay
const int MANUAL_BTN_PIN = 9;       // Physical Button
const int SOLENOID_PIN = 10;        // Compressor Valve
const int FLOW_SENSOR_PIN = 18;     // Pulse/Flow Sensor
const int RGB_LED_PIN = 48;         // NeoPixel Status

// --- THRESHOLDS & CONFIG ---
struct VoltageConfig {
  int HIGH_THRESHOLD = 250;
  int LOW_THRESHOLD = 170;
  int RESUME_GAP = 5;        // Gap needed to restart after error
  int waitSeconds = 15;      // Seconds to wait after voltage stabilizes
  int status = 1;            // 1=Safe, 0=Wait/Error
};

struct TankConfig {
  int LOW_THRESHOLD = 50;    // Pump starts at this %
  int FULL_THRESHOLD = 100;  // Pump stops at this %
  float upperHeight = 84.0;  // Max 7 Feet
  static constexpr float BUFFER_HEIGHT = 10.0; // Blind zone
  int upperInvalidCount = 0; // Max 10 fails before SNR ERR
};

struct DryRunConfig {
  int WAIT_SECONDS_SET = 30; // Flow must appear within 30s
  int error = 0;             // 0=OK, 1=Alarm, 2=Locked
  int autoRetryMinutes = 30; // Wait before auto-restart
  int retryCountdown = 0;
};

struct CoolDownConfig {
  int restMinutes = 0;       // rest after 1 hour run
  bool isResting = false;
};

struct CompressorConfig {
  int opMode = 0;            // 0=Water, 1=Air Compressor
  int valveDelay = 5;        // Seconds for venting
};

struct MasterSlaveConfig {
  int sysRole = 0;           // 0=Standalone, 1=Master, 2=Slave
  String linkedID = "";      // Master Device ID
  int settlingMinutes = 10;  // Wait for water to settle
  bool isSettling = false;
};

enum class PumpState { IDLE, PRE_START_VALVE, PUMPING, POST_STOP_VALVE, DRY_RUN_ALARM, DRY_RUN_LOCKED, SENSOR_ERROR, VOLTAGE_ERROR, VOLTAGE_WAIT, COOLING_DOWN, SETTLING_WATER };

// --- CORE SENSOR LOGIC ---
// monitorSensors() handles Ultrasonic median filtering (20 samples) 
// and Voltage ZMPT101B filtering (EMA smoothing + spike rejection).
// logic checks for valid voltage between 40V and 320V.

// --- PUMP LOGIC (updatePumpLogic) ---
// 1. If Slave: checks MQTT status of Master. Stops if Master is unsafe/pumping.
// 2. Flow Detection: checks FLOW_SENSOR_PIN. Logic LOW = Flow.
// 3. Dry-Run: If Motor is ON and no flow for 30s -> DRY_RUN_ALARM (Buzzer).
// 4. Alarm Lock: After 60s of Alarm -> DRY_RUN_LOCKED (Needs manual reset or Auto-Retry).
// 5. Voltage Guard: Stops motor immediately if Voltage > 250 or < 170.
// 6. DND Mode: Prevents auto-start during scheduled night hours.
// 7. Compressor Mode: Activates SOLENOID_PIN before motor start and after motor stop.

// --- BUTTON LOGIC (monitorButton) ---
// - Single Click: Toggles Pump ON/OFF. Resets Dry-Run Alarm. Silences SNR ERR.
// - Double Click: Shows System Info (IP, ID, License) on LCD for 10s.
// - Long Press (3s): Force starts WiFi AP Configuration Mode.

// --- NETWORK & CLOUD ---
// - WiFiManager: If no SSID saved, starts "Auto-Pump-Config" AP.
// - MQTT: Publishes JSON status to 'smartpump/DEVICE_ID/status'.
// - MQTT: Subscribes to 'smartpump/DEVICE_ID/set' for remote control.
// - Licensing: Token-based (Base64/MD5) tied to chip MAC address.

// [NOTE: HTML/CSS Dashboard and LCD custom character definitions have been stripped to save quota]
