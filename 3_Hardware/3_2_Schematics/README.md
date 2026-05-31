# Schematics

> ⚠️ **Status: documentation-first.** The reference build uses an off-the-shelf
> ESP32 dev board + breakout accelerometer wired per the table below, so no
> custom PCB is required to get started. A proper integrated board is on the
> [roadmap](../../docs/roadmap.md).

## Reference wiring (TREMORMESH-Lite)

```
            ESP32-WROOM-32
          +----------------+
   3V3 ---| 3V3        GND |--- GND
          |                |
 GPIO21 --| SDA            |
 GPIO22 --| SCL            |
          +----------------+
                |  |
              I2C bus
                |  |
          +----------------+
          |   MPU-6050     |
          | VCC SDA SCL GND|
          +----------------+
```

## Contributing a PCB

KiCad projects are welcome here. Please commit the **source** (`.kicad_sch`,
`.kicad_pcb`) and export Gerbers/PDF to `3_Hardware/3_2_Schematics/exports/`
(git-ignored - attach to releases instead of committing binaries).
