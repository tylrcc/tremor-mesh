"""Tests for the consensus engine. Run with: pytest -q"""

from __future__ import annotations

from tremormesh.consensus import ConsensusEngine, NodeTrigger

# Three well-separated Bay Area nodes.
A = dict(lat=37.7749, lon=-122.4194)
B = dict(lat=37.8044, lon=-122.2712)
C = dict(lat=37.6879, lon=-122.4702)


def test_quorum_fires_alert() -> None:
    eng = ConsensusEngine(quorum=3, window_sec=5.0)
    assert eng.ingest(NodeTrigger("a", **A, t=20.0, ratio=9.0)) is None
    assert eng.ingest(NodeTrigger("b", **B, t=20.7, ratio=7.5)) is None
    alert = eng.ingest(NodeTrigger("c", **C, t=21.3, ratio=8.1))
    assert alert is not None
    assert len(alert.node_ids) == 3


def test_below_quorum_stays_quiet() -> None:
    eng = ConsensusEngine(quorum=3, window_sec=5.0)
    eng.ingest(NodeTrigger("a", **A, t=20.0, ratio=9.0))
    assert eng.ingest(NodeTrigger("b", **B, t=20.7, ratio=7.5)) is None


def test_stale_triggers_expire_from_window() -> None:
    eng = ConsensusEngine(quorum=3, window_sec=5.0)
    eng.ingest(NodeTrigger("a", **A, t=0.0, ratio=9.0))
    eng.ingest(NodeTrigger("b", **B, t=1.0, ratio=7.5))
    # Third node arrives long after the first two have aged out.
    assert eng.ingest(NodeTrigger("c", **C, t=30.0, ratio=8.1)) is None


def test_colocated_nodes_cannot_self_confirm() -> None:
    eng = ConsensusEngine(quorum=3, window_sec=5.0, min_sep_km=0.5)
    # All three at (nearly) the same coordinates means no geographic spread.
    eng.ingest(NodeTrigger("a", lat=37.0, lon=-122.0, t=20.0, ratio=9.0))
    eng.ingest(NodeTrigger("b", lat=37.0001, lon=-122.0001, t=20.5, ratio=8.0))
    alert = eng.ingest(
        NodeTrigger("c", lat=37.0002, lon=-122.0002, t=21.0, ratio=8.0))
    assert alert is None


def test_cooldown_suppresses_repeat() -> None:
    eng = ConsensusEngine(quorum=3, window_sec=5.0, cooldown_sec=30.0)
    eng.ingest(NodeTrigger("a", **A, t=20.0, ratio=9.0))
    eng.ingest(NodeTrigger("b", **B, t=20.7, ratio=7.5))
    assert eng.ingest(NodeTrigger("c", **C, t=21.3, ratio=8.1)) is not None
    # A second burst 2 s later is inside the cooldown, so it is suppressed.
    eng.ingest(NodeTrigger("a", **A, t=23.0, ratio=9.0))
    eng.ingest(NodeTrigger("b", **B, t=23.5, ratio=7.5))
    assert eng.ingest(NodeTrigger("c", **C, t=24.0, ratio=8.1)) is None
