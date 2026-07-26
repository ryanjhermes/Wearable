#include <Arduino.h>
#include <Wire.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "MAX30105.h"

// Raw IR waveform capture for HR-algorithm development. Streams the MAX30102 IR
// channel at ~SAMPLE_HZ over BLE, batched. Wear it near the Mac and run
// scripts/raw_ir_capture.py to record the true wrist PPG signal so we can design
// a proper band-pass + autocorrelation HR estimator against real data.
//
// No flash logging on purpose: raw IR at ~100 Hz fills 512 KB in ~minutes, and
// this is a diagnostic — the Mac captures. The client auto-reconnects on drops
// (you'll get a gap, not a crash). Advertises as "Wearable-IR" (distinct from the
// HR firmware's "Wearable-HR").

MAX30105 particleSensor;

// ========================= CONFIG — tune here ==========================
static const byte SAMPLE_AVG  = 4;      // on-chip sample averaging
static const int  SAMPLE_RATE = 400;    // Hz before averaging
static const int  PULSE_WIDTH = 411;    // us (max ADC resolution)
static const int  ADC_RANGE   = 16384;  // full-scale range
static const byte LED_MODE    = 2;      // 1=Red, 2=Red+IR, 3=+Green
static const byte RED_AMP     = 0x1F;   // LED current — perfusion at the wrist
static const int  BATCH       = 10;     // IR samples per BLE notify
static const int  SAMPLE_HZ   = SAMPLE_RATE / SAMPLE_AVG;  // effective (~100 Hz)
// =======================================================================

static const char *TELEM_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E";
static const char *TELEM_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E";
static const char *DEVICE_NAME = "Wearable-IR";

BLECharacteristic *telemChar = nullptr;
bool deviceConnected = false;
bool sensor_ok = false;

long batch[BATCH];
int batchN = 0;
unsigned long batchStartMs = 0;

// serial heartbeat
long lastStatus = 0;
unsigned long samplesTotal = 0;

class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *s) { deviceConnected = true; }
  void onDisconnect(BLEServer *s) {
    deviceConnected = false;
    BLEDevice::startAdvertising();
  }
};

void setupBle() {
  BLEDevice::init(DEVICE_NAME);
  BLEDevice::setPower(ESP_PWR_LVL_P9, ESP_BLE_PWR_TYPE_DEFAULT);
  BLEDevice::setPower(ESP_PWR_LVL_P9, ESP_BLE_PWR_TYPE_ADV);
  BLEServer *server = BLEDevice::createServer();
  server->setCallbacks(new ServerCallbacks());
  BLEService *svc = server->createService(TELEM_SERVICE_UUID);
  telemChar = svc->createCharacteristic(
      TELEM_CHAR_UUID,
      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  telemChar->addDescriptor(new BLE2902());
  svc->start();
  BLEAdvertising *adv = BLEDevice::getAdvertising();
  adv->addServiceUUID(TELEM_SERVICE_UUID);
  adv->setScanResponse(true);
  BLEDevice::startAdvertising();
  Serial.println("BLE advertising as \"Wearable-IR\"");
  Serial.println("Mac: python scripts/raw_ir_capture.py");
}

// Notify one batch: "t_start_ms,hz,ir0,ir1,...". The Mac reconstructs each
// sample's time as t_start + i*(1000/hz).
void sendBatch() {
  if (deviceConnected && telemChar != nullptr && batchN > 0) {
    char buf[220];
    int n = snprintf(buf, sizeof(buf), "%lu,%d", batchStartMs, SAMPLE_HZ);
    for (int i = 0; i < batchN; i++)
      n += snprintf(buf + n, sizeof(buf) - n, ",%ld", batch[i]);
    telemChar->setValue((uint8_t *)buf, strlen(buf));
    telemChar->notify();
  }
  batchN = 0;
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("MAX30102 raw IR capture");
  setupBle();

  if (particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    sensor_ok = true;
    particleSensor.setup(RED_AMP, SAMPLE_AVG, LED_MODE, SAMPLE_RATE, PULSE_WIDTH,
                         ADC_RANGE);
    particleSensor.setPulseAmplitudeRed(RED_AMP);
    particleSensor.setPulseAmplitudeGreen(0);
    Serial.print("Sensor ready @ ~");
    Serial.print(SAMPLE_HZ);
    Serial.println(" Hz. Wear on wrist, stay reasonably still.");
  } else {
    Serial.println("MAX30102 not found at 0x57 — check wiring.");
  }
}

void loop() {
  if (!sensor_ok) {
    delay(100);
    return;
  }

  particleSensor.check();  // pull any new FIFO samples
  while (particleSensor.available()) {
    long ir = particleSensor.getFIFOIR();
    particleSensor.nextSample();
    if (batchN == 0) batchStartMs = millis();
    batch[batchN++] = ir;
    samplesTotal++;
    if (batchN >= BATCH) sendBatch();
  }

  if (millis() - lastStatus >= 2000) {
    lastStatus = millis();
    Serial.print("ir_samples=");
    Serial.print(samplesTotal);
    Serial.print("  ble=");
    Serial.println(deviceConnected ? "connected" : "advertising");
  }
}
