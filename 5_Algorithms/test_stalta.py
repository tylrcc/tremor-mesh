"""Tests validating the reference detector. Run with: pytest -q"""

from __future__ import annotations

import numpy as np

from tremormesh.stalta import StaLtaConfig, detect
from tremormesh.synthetic import synthetic_seismogram


def test_detects_p_wave_near_onset() -> None:
    cfg = StaLtaConfig()
    sig, meta = synthetic_seismogram(cfg.fs)
    triggers = detect(sig, cfg)
    assert triggers, "expected at least one trigger on a synthetic quake"
    on_time = triggers[0].on_time
    # The P-wave is injected at meta['p_time']; detection should land within
    # ~1 s after onset (STA window + threshold crossing latency).
    assert meta["p_time"] <= on_time <= meta["p_time"] + 1.0


def test_warning_lead_is_positive() -> None:
    cfg = StaLtaConfig()
    sig, meta = synthetic_seismogram(cfg.fs)
    triggers = detect(sig, cfg)
    lead = meta["s_time"] - triggers[0].on_time
    assert lead > 0, "detection must precede the destructive S-wave"


def test_no_trigger_on_pure_noise() -> None:
    cfg = StaLtaConfig()
    rng = np.random.default_rng(7)
    noise = rng.normal(0.0, 0.02, int(60 * cfg.fs))
    triggers = detect(noise, cfg)
    assert not triggers, "ambient noise must not trip the detector"


def test_config_window_sample_counts() -> None:
    cfg = StaLtaConfig(fs=100.0, sta_sec=0.5, lta_sec=10.0)
    assert cfg.nsta == 50
    assert cfg.nlta == 1000
