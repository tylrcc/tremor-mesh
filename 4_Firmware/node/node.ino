/*
 * TREMORMESH node firmware  -  ESP32 + MPU-6050/ADXL345
 * ---------------------------------------------------------------------------
 * Reads a MEMS accelerometer at a fixed rate, runs the SAME recursive STA/LTA
 * trigger as tremormesh/stalta.py, and publishes a compact JSON trigger over
 * MQTT when ground motion is detected. Everything runs in O(1) memory and
 * constant time per sample, so an $5 ESP32 keeps up indefinitely.
 *
 * Wire-compatible payload (topic: tremormesh/trigger):
 *   {"id":"node-a1","lat":37.7749,"lon":-122.4194,"t":1717029384.12,"ratio":9.4}
 *
 * Dependencies (Arduino Library Manager):
 *   - Adafruit MPU6050, Adafruit Unified Sensor
 *   - PubSubClient (MQTT)
 *
 * License: MIT (see LICENSE-MIT). Hardware design files are CERN-OHL-P.
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// ----------------------------- configuration ------------------------------
static const char*  NODE_ID   = "node-a1";
static const float  NODE_LAT  = 37.7749f;   // set to this node's location
static const float  NODE_LON  = -122.4194f;

static const char*  WIFI_SSID = "your-ssid";
static const char*  WIFI_PASS = "your-pass";
static const char*  MQTT_HOST = "192.168.1.10";
static const int    MQTT_PORT = 1883;
static const char*  MQTT_TOPIC = "tremormesh/trigger";

// Detector parameters - keep in lock-step with StaLtaConfig in Python.
static const float  FS       = 100.0f;   // Hz sample rate
static const float  STA_SEC  = 0.5f;
static const float  LTA_SEC  = 10.0f;
static const float  THR_ON   = 4.0f;
static const float  THR_OFF  = 1.5f;

// --------------------------------------------------------------------------
WiFiClient        wifiClient;
PubSubClient      mqtt(wifiClient);
Adafruit_MPU6050  imu;

// Recursive STA/LTA state (mirrors recursive_sta_lta()).
const float CSTA = 1.0f / (STA_SEC * FS);
const float CLTA = 1.0f / (LTA_SEC * FS);
float sta = 0.0f;
float lta = 1e-6f;     // tiny non-zero seed avoids div-by-zero on boot
float dcBias = 0.0f;   // slow DC tracker to remove gravity / offset
bool  triggerActive = false;
float peakRatio = 0.0f;

const uint32_t SAMPLE_US = (uint32_t)(1e6f / FS);
uint32_t nextSampleUs = 0;

// Approximate wall-clock seconds since boot (good enough for windowing;
// swap in NTP/GPS time for cross-node alignment in production).
float nowSeconds() { return millis() / 1000.0f; }

void connectWifi() {
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(250); }
}

void connectMqtt() {
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  while (!mqtt.connected()) {
    if (mqtt.connect(NODE_ID)) break;
    delay(500);
  }
}

void publishTrigger(float ratio) {
  char payload[160];
  snprintf(payload, sizeof(payload),
           "{\"id\":\"%s\",\"lat\":%.6f,\"lon\":%.6f,\"t\":%.2f,\"ratio\":%.1f}",
           NODE_ID, NODE_LAT, NODE_LON, nowSeconds(), ratio);
  mqtt.publish(MQTT_TOPIC, payload);
}

// Vertical-axis magnitude is enough for a first cut; production firmware
// fuses all three axes. We track a slow DC bias and use the residual energy
// as the characteristic function, exactly like the Python reference.
float readCharacteristicFunction() {
  sensors_event_t a, g, temp;
  imu.getEvent(&a, &g, &temp);
  float z = a.acceleration.z;            // m/s^2
  dcBias += 0.001f * (z - dcBias);       // ~10 s high-pass at 100 Hz
  float residual = z - dcBias;
  return residual * residual;            // energy
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  if (!imu.begin()) {
    Serial.println("MPU6050 not found - check wiring");
    while (true) delay(1000);
  }
  imu.setAccelerometerRange(MPU6050_RANGE_2_G);
  imu.setFilterBandwidth(MPU6050_BAND_44_HZ);

  connectWifi();
  connectMqtt();
  nextSampleUs = micros();
  Serial.printf("TREMORMESH node %s online @ %.0f Hz\n", NODE_ID, FS);
}

void loop() {
  if (!mqtt.connected()) connectMqtt();
  mqtt.loop();

  uint32_t now = micros();
  if ((int32_t)(now - nextSampleUs) < 0) return;   // not time for a sample yet
  nextSampleUs += SAMPLE_US;

  float cf = readCharacteristicFunction();
  sta += CSTA * (cf - sta);
  lta += CLTA * (cf - lta);
  float ratio = (lta > 1e-9f) ? (sta / lta) : 1.0f;

  // Trigger state machine with hysteresis (matches detect()).
  if (!triggerActive && ratio >= THR_ON) {
    triggerActive = true;
    peakRatio = ratio;
    publishTrigger(ratio);
    Serial.printf("TRIGGER ratio=%.1f t=%.2f\n", ratio, nowSeconds());
  } else if (triggerActive) {
    if (ratio > peakRatio) peakRatio = ratio;
    if (ratio <= THR_OFF) triggerActive = false;
  }
}
