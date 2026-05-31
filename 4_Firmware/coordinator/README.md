# Coordinator / Gateway

The coordinator is **not** a microcontroller sketch - it runs on any always-on
host (a Raspberry Pi is ideal) and bridges node triggers into the consensus
engine.

➡️ The implementation lives in [`6_Server/`](../../6_Server):

- [`gateway.py`](../../6_Server/gateway.py) - MQTT subscriber → consensus.
- [`consensus.py`](../../6_Server/consensus.py) - quorum + geo-spread logic.

## Minimal Pi setup

```bash
sudo apt install -y mosquitto mosquitto-clients python3-pip
pip install -r requirements.txt paho-mqtt
python 6_Server/gateway.py --host localhost
```

Point your nodes' `MQTT_HOST` at the Pi's IP and you have a working local mesh.
For a **LoRa** concentrator instead of Wi-Fi/MQTT, feed decoded packets into the
same `NodeTrigger` interface - the consensus engine is transport-agnostic.
