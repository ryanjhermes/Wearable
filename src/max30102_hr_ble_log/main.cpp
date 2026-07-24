#include <Arduino.h>
#include <Wire.h>
#include <LittleFS.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "MAX30105.h"
#include "heartRate.h"

// MAX30102 HR — store-and-forward: log every 1 Hz sample to LittleFS AND stream
// over BLE. Telemetry always flows through the flash cursor, so an offline gap is
// buffered and back-filled to the Mac the moment it reconnects.
//
// Data path (single, unified):
//   sample -> append to /hr_log.csv (flash) -> drain from a persisted send-cursor
//             over BLE telemetry when connected -> compact flash once caught up.
//
// No app-layer acks: the cursor advances as each line is notified. A full
// disconnect resumes cleanly from the cursor; only the single in-flight line can
// be lost on an abrupt drop (negligible at 1 Hz). See CLAUDE.md.
//
// BLE (device "Wearable-HR"):
//   Standard Heart Rate (0x180D) — live avg BPM for generic HR apps
//   Custom telemetry (Nordic-UART UUIDs) — CSV notify: t_ms,avg_bpm,last_bpm,beats,ir,finger
// Connect from Mac: python scripts/ble_hr_stream.py
//
// USB serial commands (type + Enter): d=dump log  e=erase log  i=info

MAX30105 particleSensor;

// ========================= CONFIG — tune here ==========================
// Reporting / logging cadence. Beat detection ALWAYS samples IR every loop();
// this only throttles the append + BLE notify + serial line. Changing it does
// NOT change the BPM math — inter-beat intervals are timed continuously.
static const long SAMPLE_INTERVAL_MS = 3000;    // one row every N ms

// Heart-rate detection
static const long FINGER_IR_THRESHOLD = 50000;  // IR below this = "no finger"
static const int  BPM_MIN = 20;                 // reject beats outside this band
static const int  BPM_MAX = 255;
static const unsigned long BPM_WINDOW_MS = 30000;  // avg BPM over the last N ms of beats
static const int  BEAT_CAP = 200;               // max beats held (>= BPM_MAX over the window)
static const byte RED_PULSE_AMPLITUDE = 0x1F;   // MAX30102 LED current 0x00-0xFF

// BLE
static const char *DEVICE_NAME = "Wearable-HR";
static const esp_power_level_t BLE_TX_POWER = ESP_PWR_LVL_P9;  // +9 dBm (max) for range
// Connection params applied on connect (survive brief RF fades before dropping):
static const uint16_t CONN_INTERVAL_MIN = 0x10;  // 20 ms  (units of 1.25 ms)
static const uint16_t CONN_INTERVAL_MAX = 0x20;  // 40 ms
static const uint16_t CONN_LATENCY = 0;
static const uint16_t CONN_TIMEOUT = 600;        // 6 s supervision (units of 10 ms)

// Flash buffer (store-and-forward)
static const char *LOG_PATH = "/hr_log.csv";
static const char *OFF_PATH = "/hr_sent.off";
static const char *CSV_HEADER = "t_ms,avg_bpm,last_bpm,beats,ir,finger";
static const size_t MAX_LOG_BYTES = 512 * 1024;  // hard cap while offline
static const size_t COMPACT_BYTES = 64 * 1024;   // reclaim flash once drained past this

// BLE back-fill pacing (burst speed when emptying the buffer on reconnect)
static const int LINES_PER_DRAIN = 5;            // lines per loop() during back-fill
static const int NOTIFY_GAP_MS = 10;             // gap between back-fill notifies
// =======================================================================

// ---- runtime state (not config) ----
// Ring buffer of recent beat timestamps → avg BPM over the last BPM_WINDOW_MS.
unsigned long beatTimes[BEAT_CAP];
int beatHead = 0;         // next write slot
int beatStored = 0;       // beats currently held (<= BEAT_CAP)
long lastBeat = 0;
float beatsPerMinute = 0; // instantaneous (last interval)
int beatAvg = 0;          // windowed average

bool sensor_ok = false;
bool fs_ok = false;
bool logging = true;

long lastSample = 0;
int beatsThisWindow = 0;

size_t sentOffset = 0;      // bytes of LOG already streamed over BLE
long lastOffsetSave = 0;    // throttle cursor persistence

bool deviceConnected = false;
bool oldDeviceConnected = false;
long connectedAt = 0;       // for a short post-connect subscribe grace

static const char *HR_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb";
static const char *HR_MEAS_CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb";
static const char *TELEM_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E";
static const char *TELEM_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E";

BLECharacteristic *hrChar = nullptr;
BLECharacteristic *telemChar = nullptr;
BLEServer *bleServer = nullptr;

class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *server, esp_ble_gatts_cb_param_t *param) {
    deviceConnected = true;
    connectedAt = millis();
    // Ask the central for a longer supervision timeout so a brief RF fade
    // (walking a few feet away) doesn't drop the link.
    server->updateConnParams(param->connect.remote_bda, CONN_INTERVAL_MIN,
                             CONN_INTERVAL_MAX, CONN_LATENCY, CONN_TIMEOUT);
  }
  void onDisconnect(BLEServer *server) {
    deviceConnected = false;
    BLEDevice::startAdvertising();
  }
};

// ---- Flash helpers ------------------------------------------------------
size_t logSize() {
  if (!fs_ok || !LittleFS.exists(LOG_PATH)) return 0;
  File f = LittleFS.open(LOG_PATH, "r");
  if (!f) return 0;
  size_t s = f.size();
  f.close();
  return s;
}

// Create the file with a header if missing/empty. Returns the header length so
// callers can park the send-cursor past it (header is never streamed).
size_t ensureLogHeader() {
  if (!fs_ok) return 0;
  size_t existing = logSize();
  if (existing > 0) return existing;  // already has header (and maybe data)
  File f = LittleFS.open(LOG_PATH, "w");
  if (!f) {
    Serial.println("Failed to create log file.");
    fs_ok = false;
    return 0;
  }
  f.println(CSV_HEADER);
  size_t s = f.size();
  f.close();
  return s;
}

void saveOffset() {
  if (!fs_ok) return;
  File f = LittleFS.open(OFF_PATH, "w");
  if (!f) return;
  f.print(sentOffset);
  f.close();
}

void loadOffset(size_t headerLen) {
  sentOffset = headerLen;  // default: skip the header
  if (!fs_ok || !LittleFS.exists(OFF_PATH)) return;
  File f = LittleFS.open(OFF_PATH, "r");
  if (!f) return;
  String s = f.readStringUntil('\n');
  f.close();
  size_t v = (size_t)s.toInt();
  size_t sz = logSize();
  if (v <= sz) sentOffset = v;  // clamp against a shorter/erased file
}

void appendLogLine(unsigned long t_ms, int avg, float last, int beats, long ir,
                   bool finger) {
  if (!fs_ok || !logging) return;
  if (logSize() >= MAX_LOG_BYTES) {
    logging = false;
    Serial.println("Log full — pausing writes until drained/compacted.");
    return;
  }
  File f = LittleFS.open(LOG_PATH, "a");
  if (!f) {
    Serial.println("Log append failed.");
    return;
  }
  f.print(t_ms);
  f.print(',');
  f.print(avg);
  f.print(',');
  f.print(last, 1);
  f.print(',');
  f.print(beats);
  f.print(',');
  f.print(ir);
  f.print(',');
  f.println(finger ? 1 : 0);
  f.close();
}

// Stream up to LINES_PER_DRAIN lines from the cursor over BLE telemetry.
void drainToBle() {
  if (!deviceConnected || telemChar == nullptr) return;
  if (millis() - connectedAt < 1500) return;  // let the client subscribe first

  size_t sz = logSize();
  if (sentOffset >= sz) return;  // caught up — nothing to send

  File f = LittleFS.open(LOG_PATH, "r");
  if (!f) return;
  if (!f.seek(sentOffset)) {
    f.close();
    return;
  }

  for (int i = 0; i < LINES_PER_DRAIN && deviceConnected; i++) {
    String line = f.readStringUntil('\n');
    if (line.length() == 0 && !f.available()) break;  // EOF
    size_t consumed = line.length() + 1;              // include the '\n'
    line.trim();
    if (line.length() > 0) {
      telemChar->setValue((uint8_t *)line.c_str(), line.length());
      telemChar->notify();
    }
    sentOffset += consumed;
    if (sentOffset > sz) sentOffset = sz;
    delay(NOTIFY_GAP_MS);
  }
  f.close();
}

// Once every buffered line has been streamed and the file is large, reclaim
// flash by rewriting it to just a header. Safe: sentOffset >= size means no
// undelivered data. Re-enables logging if it had stopped on a full cap.
void compactIfDrained() {
  if (!deviceConnected) return;
  size_t sz = logSize();
  if (sz < COMPACT_BYTES) return;
  if (sentOffset < sz) return;  // still data to send
  if (LittleFS.exists(LOG_PATH)) LittleFS.remove(LOG_PATH);
  size_t headerLen = ensureLogHeader();
  sentOffset = headerLen;
  logging = true;
  saveOffset();
  Serial.println("Flash compacted after full drain.");
}

// ---- BLE notify ---------------------------------------------------------
void notifyHeartRate(int bpm) {
  if (!deviceConnected || hrChar == nullptr) return;
  uint8_t pkt[2];
  pkt[0] = 0x00;  // flags: uint8 BPM
  pkt[1] = (uint8_t)constrain(bpm, 0, 255);
  hrChar->setValue(pkt, sizeof(pkt));
  hrChar->notify();
}

void setupBle() {
  BLEDevice::init(DEVICE_NAME);
  // Max radio power on the advertising, scan-response, and connection paths.
  BLEDevice::setPower(BLE_TX_POWER, ESP_BLE_PWR_TYPE_DEFAULT);
  BLEDevice::setPower(BLE_TX_POWER, ESP_BLE_PWR_TYPE_ADV);
  BLEDevice::setPower(BLE_TX_POWER, ESP_BLE_PWR_TYPE_SCAN);
  bleServer = BLEDevice::createServer();
  bleServer->setCallbacks(new ServerCallbacks());

  BLEService *hrService = bleServer->createService(HR_SERVICE_UUID);
  hrChar = hrService->createCharacteristic(
      HR_MEAS_CHAR_UUID,
      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  hrChar->addDescriptor(new BLE2902());
  hrService->start();

  BLEService *telemService = bleServer->createService(TELEM_SERVICE_UUID);
  telemChar = telemService->createCharacteristic(
      TELEM_CHAR_UUID,
      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  telemChar->addDescriptor(new BLE2902());
  telemService->start();

  BLEAdvertising *adv = BLEDevice::getAdvertising();
  adv->addServiceUUID(HR_SERVICE_UUID);
  adv->addServiceUUID(TELEM_SERVICE_UUID);
  adv->setScanResponse(true);
  BLEDevice::startAdvertising();

  Serial.println("BLE advertising as \"Wearable-HR\"");
  Serial.println("Mac: python scripts/ble_hr_stream.py");
}

// ---- USB serial commands (debug / manual dump) --------------------------
void printInfo() {
  if (!fs_ok) {
    Serial.println("FS not mounted.");
    return;
  }
  Serial.print("LittleFS used=");
  Serial.print(LittleFS.usedBytes());
  Serial.print("/");
  Serial.print(LittleFS.totalBytes());
  Serial.print("  log=");
  Serial.print(logSize());
  Serial.print(" bytes  sent=");
  Serial.print(sentOffset);
  Serial.print("  logging=");
  Serial.print(logging ? "on" : "off");
  Serial.print("  ble=");
  Serial.println(deviceConnected ? "connected" : "advertising");
}

void dumpLog() {
  if (!fs_ok || !LittleFS.exists(LOG_PATH)) {
    Serial.println("No log file yet.");
    return;
  }
  File f = LittleFS.open(LOG_PATH, "r");
  if (!f) return;
  Serial.println("---FLASH_DUMP_BEGIN---");
  while (f.available()) Serial.write(f.read());
  f.close();
  Serial.println("---FLASH_DUMP_END---");
}

void eraseLog() {
  if (!fs_ok) return;
  if (LittleFS.exists(LOG_PATH)) LittleFS.remove(LOG_PATH);
  size_t headerLen = ensureLogHeader();
  sentOffset = headerLen;
  logging = true;
  saveOffset();
  Serial.println("Log erased.");
  printInfo();
}

void handleSerialCommands() {
  static String buf;
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      buf.trim();
      if (buf.equalsIgnoreCase("d")) dumpLog();
      else if (buf.equalsIgnoreCase("e")) eraseLog();
      else if (buf.equalsIgnoreCase("i")) printInfo();
      buf = "";
    } else {
      buf += c;
      if (buf.length() > 16) buf = "";
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("MAX30102 HR — BLE store-and-forward");

  setupBle();

  fs_ok = LittleFS.begin(true);  // format once if mount fails
  if (!fs_ok) {
    Serial.println("LittleFS mount failed.");
  } else {
    size_t headerLen = ensureLogHeader();
    loadOffset(headerLen);
    Serial.println("LittleFS ready.");
    printInfo();
  }

  if (particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    sensor_ok = true;
    particleSensor.setup();
    particleSensor.setPulseAmplitudeRed(RED_PULSE_AMPLITUDE);
    particleSensor.setPulseAmplitudeGreen(0);
    Serial.println("Sensor ready. Rest fingertip lightly.");
  } else {
    Serial.println("MAX30102 not found at 0x57 — check wiring.");
  }
}

// ---- Windowed BPM: average over beats seen in the last BPM_WINDOW_MS -------
void recordBeat(unsigned long t) {
  beatTimes[beatHead] = t;
  beatHead = (beatHead + 1) % BEAT_CAP;
  if (beatStored < BEAT_CAP) beatStored++;
}

void resetBeatWindow() {
  beatHead = 0;
  beatStored = 0;
}

// BPM = 60000 * (beats-1) / (span of those beats). Uses only beats inside the
// window; needs >= 2 to produce a value. Overflow-safe: compares nowMs - t.
int windowedBpm(unsigned long nowMs) {
  unsigned long oldest = 0, newest = 0;
  int n = 0;
  for (int i = 0; i < beatStored; i++) {
    unsigned long t = beatTimes[i];
    if ((unsigned long)(nowMs - t) <= BPM_WINDOW_MS) {
      if (n == 0 || t < oldest) oldest = t;
      if (n == 0 || t > newest) newest = t;
      n++;
    }
  }
  if (n < 2 || newest == oldest) return 0;
  return (int)lround(60000.0 * (n - 1) / (double)(newest - oldest));
}

void loop() {
  handleSerialCommands();

  if (!sensor_ok) {
    delay(100);
    return;
  }

  long irValue = particleSensor.getIR();
  bool beat = checkForBeat(irValue);

  if (beat) {
    unsigned long nowMs = millis();
    if (lastBeat != 0) {
      long delta = nowMs - lastBeat;
      beatsPerMinute = 60000.0 / delta;
      // Only plausible beats enter the 30 s window (rejects noise/double-taps).
      if (beatsPerMinute < BPM_MAX && beatsPerMinute > BPM_MIN) {
        recordBeat(nowMs);
      }
    }
    lastBeat = nowMs;
    beatsThisWindow++;
  }

  beatAvg = windowedBpm(millis());

  bool finger = irValue >= FINGER_IR_THRESHOLD;
  if (!finger) {
    beatsPerMinute = 0;
    beatAvg = 0;
    resetBeatWindow();
  }

  // Every SAMPLE_INTERVAL_MS: append to flash, notify the standard HR service,
  // echo to USB. Telemetry itself is streamed by drainToBle() from the flash
  // cursor, so the just-appended line goes out the same path (immediately when
  // caught up).
  if (millis() - lastSample >= SAMPLE_INTERVAL_MS) {
    lastSample = millis();
    int beats = beatsThisWindow;
    beatsThisWindow = 0;

    appendLogLine(millis(), beatAvg, beatsPerMinute, beats, irValue, finger);
    notifyHeartRate(beatAvg);

    Serial.print(millis());
    Serial.print(',');
    Serial.print(beatAvg);
    Serial.print(',');
    Serial.print(beatsPerMinute, 1);
    Serial.print(',');
    Serial.print(beats);
    Serial.print(',');
    Serial.print(irValue);
    Serial.print(',');
    Serial.print(finger ? 1 : 0);
    Serial.print("  ble=");
    Serial.print(deviceConnected ? "connected" : "advertising");
    Serial.print("  buffered=");
    Serial.println(logSize() - sentOffset);
  }

  drainToBle();
  compactIfDrained();

  if (deviceConnected && millis() - lastOffsetSave >= 5000) {
    lastOffsetSave = millis();
    saveOffset();
  }

  if (!deviceConnected && oldDeviceConnected) {
    saveOffset();
    delay(500);  // let BLE stack finish disconnect
    BLEDevice::startAdvertising();
    Serial.println("BLE client disconnected — advertising again");
  }
  oldDeviceConnected = deviceConnected;
}
