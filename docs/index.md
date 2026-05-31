# TREMORMESH Documentation

> A $15 seismometer in every home - a crowd-powered earthquake early-warning mesh.

## Start here

- **[Project Description](../1_Project_Description/PROJECT.md)** - the problem, the bet, the honest limitations.
- **[System Architecture](../2_System_Architecture/ARCHITECTURE.md)** - how nodes, gateway, and consensus fit together.
- **[Bill of Materials](../3_Hardware/3_1_BOM/BOM.md)** - build a node for ~$15.

## Build & run

- **[Node firmware](../4_Firmware/node/README.md)** - flash an ESP32.
- **[Coordinator / gateway](../4_Firmware/coordinator/README.md)** - bridge triggers to consensus.
- **Reference algorithm** - `5_Algorithms/` (`python demo.py`, `pytest`).
- **Server** - `6_Server/` (consensus + MQTT gateway).
- **Simulation** - `7_Simulations/network_sim.py` (whole pipeline, no hardware).

## Deeper

- **[Roadmap](roadmap.md)** - what's next and what's hard.
- **[Licensing rationale](licensing.md)** - why hardware and software are licensed separately.
