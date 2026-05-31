# Bill of Materials - TREMORMESH Node

Two build tiers. The **Lite** node is the "$15 seismometer" headline build;
the **Pro** node swaps in a low-noise 24-bit accelerometer and a LoRa radio
for off-grid, research-grade deployments. Prices are rough single-unit street
prices and fall sharply in volume.

## TREMORMESH-Lite (~$15)

| # | Component | Example part | Qty | ~Unit $ |
|---|-----------|--------------|----:|--------:|
| 1 | MCU + Wi-Fi | ESP32-WROOM-32 dev board | 1 | 5.00 |
| 2 | Accelerometer | MPU-6050 (6-axis IMU) | 1 | 2.50 |
| 3 | USB power supply | 5 V / 1 A wall adapter | 1 | 3.00 |
| 4 | MicroUSB cable | - | 1 | 1.50 |
| 5 | Enclosure | 3D-printed (see `3_3_Enclosure/`) | 1 | 1.00 |
| 6 | Misc | dupont wires, mounting pad | - | 2.00 |
| | | | **Total** | **~$15** |

## TREMORMESH-Pro (~$55)

| # | Component | Example part | Qty | ~Unit $ |
|---|-----------|--------------|----:|--------:|
| 1 | MCU + Wi-Fi | ESP32-WROOM-32 dev board | 1 | 5.00 |
| 2 | Accelerometer | ADXL355 (low-noise 24-bit) | 1 | 30.00 |
| 3 | LoRa radio | RFM95W (868/915 MHz) | 1 | 8.00 |
| 4 | RTC / time sync | DS3231 (or GPS PPS) | 1 | 3.00 |
| 5 | Power | 5 V supply + 18650 backup | 1 | 6.00 |
| 6 | Enclosure | IP54 printed/ABS box | 1 | 3.00 |
| | | | **Total** | **~$55** |

## Notes

- **Coupling matters more than the sensor.** Bolt or epoxy the node to a
  structural element (slab, foundation, load-bearing wall). A unit sitting
  loose on a desk mostly measures the desk.
- The **MPU-6050** is noisy but, in a dense mesh, *density beats sensitivity* -
  many cheap nodes outperform a few expensive ones for early warning.
- For cross-node time alignment, prefer NTP (Lite) or GPS-PPS / DS3231 (Pro).
  Consensus tolerates a few hundred ms of skew; sub-second is plenty.
