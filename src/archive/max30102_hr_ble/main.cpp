#include <Arduino.h>
#include <Wire.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "MAX30105.h"
#include "heartRate.h"

// MAX30102 HR + BLE stream (battery / untethered). USB serial still works when plugged in.
//
// BLE services:
//   Standard Heart Rate (0x180D) — avg BPM, works with generic HR apps
//   Custom telemetry (Wearable) — CSV notify: t_ms,avg_bpm,last_bpm,beats,ir,finger
//
// Connect from Mac: python scripts/ble_hr_stream.py

MAX30105 particleSensor;

const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute = 0;
int beatAvg = 0;

bool sensor_ok = false;
bool deviceConnected = false;
bool oldDeviceConnected = false;

long lastNotify = 0;
int beatsThisSecond = 0;

// Standard Heart Rate Service
static const char *HR_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb";
static const char *HR_MEAS_CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb";

// Custom Wearable telemetry (Nordic UART-style UUIDs — widely recognized by BLE tools)
static const char *TELEM_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E";
static const char *TELEM_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E";

static const char *DEVICE_NAME = "Wearable-HR";

BLECharacteristic *hrChar = nullptr;
BLECharacteristic *telemChar = nullptr;
BLEServer *bleServer = nullptr;

class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *server) { deviceConnected = true; }

  void onDisconnect(BLEServer *server) {
    deviceConnected = false;
    BLEDevice::startAdvertising();
  }
};

void notifyHeartRate(int bpm) {
  if (!deviceConnected || hrChar == nullptr) return;

  uint8_t pkt[2];
  pkt[0] = 0x00;  // flags: uint8 BPM
  pkt[1] = (uint8_t)constrain(bpm, 0, 255);
  hrChar->setValue(pkt, sizeof(pkt));
  hrChar->notify();
}

void notifyTelemetry(unsigned long t_ms, int avg, float last, int beats, long ir,
                     bool finger) {
  if (!deviceConnected || telemChar == nullptr) return;

  char buf[80];
  snprintf(buf, sizeof(buf), "%lu,%d,%.1f,%d,%ld,%d", t_ms, avg, last, beats, ir,
           finger ? 1 : 0);
  telemChar->setValue((uint8_t *)buf, strlen(buf));
  telemChar->notify();
}

void setupBle() {
  BLEDevice::init(DEVICE_NAME);
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
      TELEM_CHAR_UUID, BLECharacteristic::PROPERTY_READ |
                           BLECharacteristic::PROPERTY_NOTIFY);
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

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("MAX30102 HR + BLE stream");

  setupBle();

  if (particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    sensor_ok = true;
    particleSensor.setup();
    particleSensor.setPulseAmplitudeRed(0x0A);
    particleSensor.setPulseAmplitudeGreen(0);
    Serial.println("Sensor ready. Rest fingertip lightly.");
  } else {
    Serial.println("MAX30102 not found at 0x57 — check wiring.");
  }
}

void loop() {
  if (!sensor_ok) {
    delay(100);
    return;
  }

  long irValue = particleSensor.getIR();
  bool beat = checkForBeat(irValue);

  if (beat) {
    if (lastBeat != 0) {
      long delta = millis() - lastBeat;
      beatsPerMinute = 60 / (delta / 1000.0);

      if (beatsPerMinute < 255 && beatsPerMinute > 20) {
        rates[rateSpot++] = (byte)beatsPerMinute;
        rateSpot %= RATE_SIZE;

        beatAvg = 0;
        for (byte x = 0; x < RATE_SIZE; x++) beatAvg += rates[x];
        beatAvg /= RATE_SIZE;
      }
    }
    lastBeat = millis();
    beatsThisSecond++;
  }

  bool finger = irValue >= 50000;
  if (!finger) {
    beatsPerMinute = 0;
    beatAvg = 0;
  }

  if (millis() - lastNotify >= 1000) {
    lastNotify = millis();
    int beats = beatsThisSecond;
    beatsThisSecond = 0;

    notifyHeartRate(beatAvg);
    notifyTelemetry(millis(), beatAvg, beatsPerMinute, beats, irValue, finger);

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
    Serial.println(deviceConnected ? "connected" : "advertising");
  }

  if (!deviceConnected && oldDeviceConnected) {
    delay(500);  // let BLE stack finish disconnect
    BLEDevice::startAdvertising();
    Serial.println("BLE client disconnected — advertising again");
  }
  oldDeviceConnected = deviceConnected;
}
