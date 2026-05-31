# Node Firmware (ESP32)

Flashes onto any ESP32 dev board wired to an MPU-6050 (Lite) or ADXL355 (Pro).

## Wiring (MPU-6050, I²C)

| MPU-6050 | ESP32 |
|----------|-------|
| VCC | 3V3 |
| GND | GND |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

## Build & flash

**Arduino IDE**
1. Install board support: *ESP32 by Espressif Systems*.
2. Library Manager → install **Adafruit MPU6050**, **Adafruit Unified Sensor**,
   **PubSubClient**.
3. Edit the `configuration` block at the top of `node.ino` (node id, location,
   Wi-Fi, MQTT broker).
4. Select your ESP32 board + port, then **Upload**.

**PlatformIO** (`platformio.ini` sketch):
```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
lib_deps =
    adafruit/Adafruit MPU6050
    adafruit/Adafruit Unified Sensor
    knolleary/PubSubClient
monitor_speed = 115200
```

## Verifying it works

Open the serial monitor at 115200 baud. Tap the surface the node is mounted to -
you should see `TRIGGER ratio=…` lines, and a matching JSON message on the
`tremormesh/trigger` MQTT topic. The detector logic here is a direct port of
[`tremormesh/stalta.py`](../../tremormesh/stalta.py); validate parameter
changes in Python first.
