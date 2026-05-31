"""Console entry points: ``tremormesh-demo`` and ``tremormesh-sim``.

These power the "try it in seconds" experience once the package is installed
with ``pip install -e .``. The same functions are called by the runnable
scripts in ``5_Algorithms/`` and ``7_Simulations/`` so behaviour is identical
whether you run from a fresh clone or an installed wheel.
"""

from __future__ import annotations

import argparse

from .consensus import ConsensusEngine, NodeTrigger
from .stalta import StaLtaConfig, detect, recursive_sta_lta
from .synthetic import synthetic_seismogram


def demo_main(argv: list[str] | None = None) -> None:
    """Single-node detection demo on a synthetic quake."""
    ap = argparse.ArgumentParser(prog="tremormesh-demo",
                                 description="TREMORMESH single-node demo")
    ap.add_argument("--plot", action="store_true",
                    help="save a PNG figure (requires matplotlib)")
    args = ap.parse_args(argv)

    cfg = StaLtaConfig()
    sig, meta = synthetic_seismogram(cfg.fs)
    triggers = detect(sig, cfg)

    print("=" * 56)
    print("  TREMORMESH single-node detection demo")
    print("=" * 56)
    print(f"  sample rate     : {cfg.fs:.0f} Hz")
    print(f"  P-wave injected : {meta['p_time']:.1f} s")
    print(f"  S-wave injected : {meta['s_time']:.1f} s  (destructive)")
    print(f"  STA/LTA windows : {cfg.sta_sec}s / {cfg.lta_sec}s  "
          f"(on={cfg.thr_on}, off={cfg.thr_off})")
    print("-" * 56)

    if not triggers:
        print("  no trigger, tune thresholds in StaLtaConfig")
        return

    first = triggers[0]
    lead = meta["s_time"] - first.on_time
    print(f"  P-wave DETECTED at : {first.on_time:.2f} s "
          f"(peak ratio {first.peak_ratio:.1f})")
    print(f"  warning lead time  : {lead:.2f} s before S-wave impact")
    print("=" * 56)

    if args.plot:
        _save_plot(sig, cfg, first.on_time)


def _save_plot(sig, cfg, detect_time) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping plot")
        return
    import numpy as np
    ratio = recursive_sta_lta(sig, cfg)
    t = np.arange(sig.size) / cfg.fs
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(9, 5))
    ax1.plot(t, sig, lw=0.6)
    ax1.set_ylabel("accel (g)")
    ax1.set_title("Synthetic seismogram")
    ax2.plot(t, ratio, color="tab:red", lw=0.8)
    ax2.axhline(cfg.thr_on, ls="--", color="k", lw=0.6, label="on")
    ax2.axvline(detect_time, color="tab:green", lw=1.2, label="detect")
    ax2.set_ylabel("STA/LTA")
    ax2.set_xlabel("time (s)")
    ax2.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig("stalta_demo.png", dpi=120)
    print("saved stalta_demo.png")


# Network simulation parameters.
_NODES = [
    ("node-1", 37.77, -122.42, 5.0),
    ("node-2", 37.80, -122.27, 12.0),
    ("node-3", 37.69, -122.47, 20.0),
    ("node-4", 37.85, -122.30, 28.0),
]
_P_VELOCITY_KMS = 6.0
_S_VELOCITY_KMS = 3.5
_ORIGIN_TIME = 10.0
_TARGET_NAME = "protected city"
_TARGET_DIST_KM = 60.0


def sim_main(argv: list[str] | None = None) -> int:
    """Full pipeline: detection across a node grid, consensus, warning lead."""
    cfg = StaLtaConfig()
    engine = ConsensusEngine(quorum=3, window_sec=8.0)

    print("=" * 64)
    print("  TREMORMESH network simulation")
    print("=" * 64)

    first_alert = None
    for node_id, lat, lon, dist in _NODES:
        p_arrival = _ORIGIN_TIME + dist / _P_VELOCITY_KMS
        s_arrival = _ORIGIN_TIME + dist / _S_VELOCITY_KMS
        sig, _ = synthetic_seismogram(cfg.fs, p_time=p_arrival, s_time=s_arrival)
        trigs = detect(sig, cfg)
        if not trigs:
            print(f"  {node_id}: no detection")
            continue
        det_t = trigs[0].on_time
        print(f"  {node_id} @ {dist:>4.0f} km : P detected at {det_t:5.2f}s "
              f"(ratio {trigs[0].peak_ratio:4.1f})")
        alert = engine.ingest(
            NodeTrigger(node_id, lat, lon, t=det_t, ratio=trigs[0].peak_ratio))
        if alert and first_alert is None:
            first_alert = alert

    print("-" * 64)
    if first_alert is None:
        print("  NO CONSENSUS ALERT, increase node density or relax quorum")
        return 1

    target_s_arrival = _ORIGIN_TIME + _TARGET_DIST_KM / _S_VELOCITY_KMS
    lead = target_s_arrival - first_alert.triggered_at
    blind_zone_km = (first_alert.triggered_at - _ORIGIN_TIME) * _S_VELOCITY_KMS

    print(f"  {first_alert}")
    print(f"  blind zone (no warning)      : ~{blind_zone_km:.0f} km radius")
    print(f"  {_TARGET_NAME} @ {_TARGET_DIST_KM:.0f} km, "
          f"S-wave at {target_s_arrival:.2f}s")
    print(f"  WARNING LEAD AT TARGET       : {lead:.2f}s before strong shaking")
    print("=" * 64)
    return 0 if lead > 0 else 1


if __name__ == "__main__":
    demo_main()
