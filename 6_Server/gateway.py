"""
MQTT -> consensus bridge.

Subscribes to ``tremormesh/trigger``, parses node payloads, runs them through
the :class:`ConsensusEngine`, and prints / forwards an alert when a quorum is
reached. Runs happily on a Raspberry Pi gateway or any always-on host.

    pip install paho-mqtt
    python gateway.py --host 192.168.1.10

If ``paho-mqtt`` is not installed (e.g. in CI), the script falls back to a
self-contained replay of a sample trigger burst so it always demonstrates the
end-to-end path.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# Allow running straight from a fresh clone (no install required).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tremormesh.consensus import Alert, ConsensusEngine, NodeTrigger  # noqa: E402


def handle_alert(alert: Alert) -> None:
    """Hook point: swap this for a webhook, siren, push notification, etc."""
    print(f"\n  >>> {alert}\n")


def parse_payload(raw: str) -> NodeTrigger | None:
    try:
        d = json.loads(raw)
        return NodeTrigger(
            node_id=str(d["id"]),
            lat=float(d["lat"]),
            lon=float(d["lon"]),
            t=float(d["t"]),
            ratio=float(d.get("ratio", 0.0)),
        )
    except (ValueError, KeyError, TypeError):
        return None


def run_mqtt(host: str, port: int, topic: str) -> None:
    import paho.mqtt.client as mqtt  # type: ignore

    engine = ConsensusEngine()

    def on_connect(client, _userdata, _flags, _rc):
        client.subscribe(topic)
        print(f"subscribed to {topic} on {host}:{port}")

    def on_message(_client, _userdata, msg):
        trig = parse_payload(msg.payload.decode("utf-8", "ignore"))
        if trig is None:
            return
        print(f"  trigger from {trig.node_id} (ratio {trig.ratio:.1f})")
        alert = engine.ingest(trig)
        if alert:
            handle_alert(alert)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, port, keepalive=60)
    client.loop_forever()


def run_replay() -> None:
    print("paho-mqtt not available - replaying a sample trigger burst\n")
    engine = ConsensusEngine()
    burst = [
        '{"id":"node-a","lat":37.7749,"lon":-122.4194,"t":20.0,"ratio":9.0}',
        '{"id":"node-b","lat":37.8044,"lon":-122.2712,"t":20.7,"ratio":7.5}',
        '{"id":"node-c","lat":37.6879,"lon":-122.4702,"t":21.3,"ratio":8.1}',
    ]
    for raw in burst:
        trig = parse_payload(raw)
        if trig is None:
            continue
        print(f"  trigger from {trig.node_id} (ratio {trig.ratio:.1f})")
        alert = engine.ingest(trig)
        if alert:
            handle_alert(alert)


def main() -> None:
    ap = argparse.ArgumentParser(description="TREMORMESH MQTT gateway")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1883)
    ap.add_argument("--topic", default="tremormesh/trigger")
    args = ap.parse_args()

    try:
        run_mqtt(args.host, args.port, args.topic)
    except ImportError:
        run_replay()


if __name__ == "__main__":
    main()
