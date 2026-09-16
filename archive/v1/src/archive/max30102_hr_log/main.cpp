#include <Arduino.h>
#include <Wire.h>
#include <LittleFS.h>
#include "MAX30105.h"
#include "heartRate.h"

// Untethered HR logger: 1 Hz CSV → LittleFS; dump/erase over USB serial.
// Commands (type in serial monitor + Enter): d=dump, e=erase, i=info

MAX30105 particleSensor;

const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute = 0;
int beatAvg = 0;

bool sensor_ok = false;
bool fs_ok = false;
bool logging = true;

long lastPrint = 0;
int beatsThisSecond = 0;

const char *LOG_PATH = "/hr_log.csv";
const size_t MAX_LOG_BYTES = 512 * 1024;  // ~hours of 1 Hz lines

void printHelp() {
  Serial.println();
  Serial.println("Commands: d=dump log  e=erase log  i=info");
  Serial.println("Unplug USB to run on battery — log keeps writing.");
  Serial.println("Plug USB back in, open monitor, press d to dump.");
}

void printInfo() {
  if (!fs_ok) {
    Serial.println("FS not mounted.");
    return;
  }
  size_t total = LittleFS.totalBytes();
  size_t used = LittleFS.usedBytes();
  size_t logSize = 0;
  if (LittleFS.exists(LOG_PATH)) {
    File f = LittleFS.open(LOG_PATH, "r");
    if (f) {
      logSize = f.size();
      f.close();
    }
  }
  Serial.print("LittleFS used=");
  Serial.print(used);
  Serial.print("/");
  Serial.print(total);
  Serial.print("  log=");
  Serial.print(logSize);
  Serial.print(" bytes  logging=");
  Serial.println(logging ? "on" : "off");
}

bool ensureLogHeader() {
  if (!fs_ok) return false;
  if (LittleFS.exists(LOG_PATH)) {
    File f = LittleFS.open(LOG_PATH, "r");
    if (f && f.size() > 0) {
      f.close();
      return true;
    }
    if (f) f.close();
  }
  File f = LittleFS.open(LOG_PATH, "w");
  if (!f) {
    Serial.println("Failed to create log file.");
    return false;
  }
  f.println("t_ms,avg_bpm,last_bpm,beats,ir,finger");
  f.close();
  return true;
}

void appendLogLine(unsigned long t_ms, int avg, float last, int beats, long ir,
                   bool finger) {
  if (!fs_ok || !logging) return;

  size_t logSize = 0;
  if (LittleFS.exists(LOG_PATH)) {
    File rf = LittleFS.open(LOG_PATH, "r");
    if (rf) {
      logSize = rf.size();
      rf.close();
    }
  }
  if (logSize >= MAX_LOG_BYTES) {
    logging = false;
    Serial.println("Log full — logging stopped. Dump (d) then erase (e).");
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

void dumpLog() {
  if (!fs_ok) {
    Serial.println("FS not mounted.");
    return;
  }
  if (!LittleFS.exists(LOG_PATH)) {
    Serial.println("No log file yet.");
    return;
  }
  File f = LittleFS.open(LOG_PATH, "r");
  if (!f) {
    Serial.println("Failed to open log.");
    return;
  }
  Serial.println("---FLASH_DUMP_BEGIN---");
  while (f.available()) {
    Serial.write(f.read());
  }
  f.close();
  Serial.println("---FLASH_DUMP_END---");
}

void eraseLog() {
  if (!fs_ok) {
    Serial.println("FS not mounted.");
    return;
  }
  if (LittleFS.exists(LOG_PATH)) {
    LittleFS.remove(LOG_PATH);
  }
  logging = true;
  if (ensureLogHeader()) {
    Serial.println("Log erased.");
  }
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
      else if (buf.length()) printHelp();
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
  Serial.println("MAX30102 HR flash logger");

  fs_ok = LittleFS.begin(true);  // format once if mount fails
  if (!fs_ok) {
    Serial.println("LittleFS mount failed.");
  } else if (!ensureLogHeader()) {
    fs_ok = false;
  } else {
    Serial.println("LittleFS ready.");
    printInfo();
  }

  if (particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    sensor_ok = true;
    particleSensor.setup();
    particleSensor.setPulseAmplitudeRed(0x0A);
    particleSensor.setPulseAmplitudeGreen(0);
    Serial.println("Sensor ready. Rest fingertip lightly.");
  } else {
    Serial.println("MAX30102 not found at 0x57 — check wiring.");
  }

  printHelp();
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

  if (millis() - lastPrint >= 1000) {
    lastPrint = millis();
    int beats = beatsThisSecond;
    beatsThisSecond = 0;

    appendLogLine(millis(), beatAvg, beatsPerMinute, beats, irValue, finger);

    // Live echo when USB is connected (harmless on battery)
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
    Serial.println(finger ? 1 : 0);
  }
}
