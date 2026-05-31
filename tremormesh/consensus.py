"""
Spatio-temporal consensus engine.

A single $15 node is noisy: a slammed door, a passing truck, or a dropped
phone all trip a single STA/LTA detector. The trick that turns a crowd of
cheap sensors into a trustworthy network is *consensus* - only believe an
event when several independent, geographically separated nodes trigger
within a short time window.

This module is transport-agnostic. Feed it ``NodeTrigger`` objects (from
MQTT, HTTP, LoRa, or a test harness) via :meth:`ConsensusEngine.ingest`; it
emits an :class:`Alert` the moment a quorum is reached. The same logic runs
on a Raspberry Pi gateway or a cloud worker.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class NodeTrigger:
    """A P-wave trigger reported by one node."""

    node_id: str
    lat: float
    lon: float
    t: float           # unix-ish timestamp of the trigger (seconds)
    ratio: float       # peak STA/LTA, a rough confidence proxy


@dataclass
class Alert:
    """A consensus-confirmed event."""

    triggered_at: float
    node_ids: list[str]
    epicenter_guess: tuple[float, float]
    mean_ratio: float

    def __str__(self) -> str:
        lat, lon = self.epicenter_guess
        return (f"ALERT @ t={self.triggered_at:.2f}s | "
                f"{len(self.node_ids)} nodes | "
                f"~epicenter ({lat:.4f}, {lon:.4f}) | "
                f"mean ratio {self.mean_ratio:.1f}")


def _haversine_km(a: NodeTrigger, b: NodeTrigger) -> float:
    """Great-circle distance between two triggers, in kilometres."""
    r = 6371.0
    p1, p2 = math.radians(a.lat), math.radians(b.lat)
    dp = math.radians(b.lat - a.lat)
    dl = math.radians(b.lon - a.lon)
    h = (math.sin(dp / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(h))


@dataclass
class ConsensusEngine:
    """Sliding-window quorum detector.

    Args:
        quorum:        Minimum distinct nodes required to confirm.
        window_sec:    Triggers must fall within this time window.
        min_sep_km:    Confirming nodes must be at least this far apart, so a
                       single rack of co-located sensors cannot self-confirm.
        cooldown_sec:  Suppress repeat alerts for this long after one fires.
    """

    quorum: int = 3
    window_sec: float = 5.0
    min_sep_km: float = 0.5
    cooldown_sec: float = 30.0

    _buffer: list[NodeTrigger] = field(default_factory=list)
    _last_alert_t: float = field(default=-1e18)

    def ingest(self, trig: NodeTrigger) -> Alert | None:
        """Add one trigger; return an Alert if it completes a quorum."""
        # Drop triggers older than the window relative to the newcomer.
        self._buffer = [t for t in self._buffer
                        if trig.t - t.t <= self.window_sec]
        self._buffer.append(trig)

        if trig.t - self._last_alert_t < self.cooldown_sec:
            return None  # still cooling down from the previous alert

        # Keep one trigger per node (the most recent) inside the window.
        latest: dict[str, NodeTrigger] = {}
        for t in self._buffer:
            if t.node_id not in latest or t.t > latest[t.node_id].t:
                latest[t.node_id] = t
        candidates = list(latest.values())

        if len(candidates) < self.quorum:
            return None

        # Require geographic spread: at least one pair separated by min_sep_km.
        spread_ok = any(
            _haversine_km(candidates[i], candidates[j]) >= self.min_sep_km
            for i in range(len(candidates))
            for j in range(i + 1, len(candidates))
        )
        if not spread_ok:
            return None

        self._last_alert_t = trig.t
        lat = sum(c.lat for c in candidates) / len(candidates)
        lon = sum(c.lon for c in candidates) / len(candidates)
        return Alert(
            triggered_at=trig.t,
            node_ids=sorted(c.node_id for c in candidates),
            epicenter_guess=(lat, lon),
            mean_ratio=sum(c.ratio for c in candidates) / len(candidates),
        )


if __name__ == "__main__":
    # Simulate three separated nodes tripping ~1 s apart -> one alert.
    eng = ConsensusEngine(quorum=3, window_sec=5.0)
    feed = [
        NodeTrigger("node-a", 37.7749, -122.4194, t=20.0, ratio=9.0),
        NodeTrigger("node-b", 37.8044, -122.2712, t=20.7, ratio=7.5),
        NodeTrigger("node-c", 37.6879, -122.4702, t=21.3, ratio=8.1),
    ]
    for trig in feed:
        alert = eng.ingest(trig)
        if alert:
            print(alert)
