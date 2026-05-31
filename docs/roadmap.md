# Roadmap

TREMORMESH is **alpha**. The detection and consensus core works in simulation;
the hard, interesting problems are the ones that make it trustworthy at scale.

## ✅ Done
- Recursive STA/LTA reference detector + tests
- Consensus engine (quorum + geographic spread + cooldown) + tests
- ESP32 node firmware mirroring the reference detector
- MQTT gateway and full-pipeline network simulation
- CI on Python 3.9 / 3.11 / 3.12

## 🔜 Next
- **Time synchronisation** - NTP on Lite nodes, GPS-PPS on Pro; quantify skew tolerance.
- **Magnitude & intensity estimate** - go from "something happened" to "expected shaking here is X".
- **Anti-spoofing** - node attestation so an attacker can't inject fake triggers to force alerts.
- **Real PCB** - replace the dev-board + dupont build with a proper board in `3_Hardware/3_2_Schematics`.
- **Alert delivery** - push notifications, MQTT fan-out, a public map.

## 🌋 Hard / research-grade
- Distinguishing local impulsive noise (door slam) from real P-waves at a single node.
- Network topology and density required for useful warning in a given region.
- Graceful behaviour under partial network partitions.
- Calibration across heterogeneous sensors and mounting quality.

Want to own one of these? See [CONTRIBUTING.md](../CONTRIBUTING.md).
