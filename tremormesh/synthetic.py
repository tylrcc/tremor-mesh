"""
Synthetic seismogram generator.

Earthquakes radiate two body waves that matter for early warning:

    * P-waves (primary)   - fast (~6 km/s), low energy, arrive *first*.
    * S-waves (secondary) - slower (~3.5 km/s), high energy, do the damage.

Because P-waves outrun S-waves, detecting the small P arrival buys you the
gap until the destructive S arrival. That gap *is* the warning. This module
fabricates a realistic single-channel acceleration trace containing ambient
noise, a P arrival, and a larger S arrival, so the detector can be exercised
deterministically without field data.
"""

from __future__ import annotations

import numpy as np


def _wavelet(n: int, fs: float, freq: float, decay: float,
             rng: np.random.Generator) -> np.ndarray:
    """A damped sinusoid burst - a crude but serviceable body-wave model."""
    t = np.arange(n) / fs
    phase = rng.uniform(0, 2 * np.pi)
    return np.sin(2 * np.pi * freq * t + phase) * np.exp(-decay * t)


def synthetic_seismogram(
    fs: float = 100.0,
    duration: float = 60.0,
    p_time: float = 20.0,
    s_time: float = 27.0,
    noise: float = 0.02,
    p_amp: float = 0.25,
    s_amp: float = 1.0,
    seed: int = 42,
) -> tuple[np.ndarray, dict]:
    """Return ``(signal, meta)`` for a fabricated earthquake.

    Args:
        fs:        Sample rate (Hz).
        duration:  Total trace length (s).
        p_time:    P-wave onset (s).
        s_time:    S-wave onset (s).
        noise:     Std-dev of ambient gaussian noise (g).
        p_amp:     Peak P-wave acceleration (g).
        s_amp:     Peak S-wave acceleration (g).
        seed:      RNG seed for reproducibility.

    Returns:
        signal: 1-D acceleration array in g.
        meta:   dict with the ground-truth arrival times.
    """
    rng = np.random.default_rng(seed)
    n = int(round(duration * fs))
    sig = rng.normal(0.0, noise, n)

    # P arrival: short, higher-frequency, modest amplitude.
    p_i = int(round(p_time * fs))
    p_len = n - p_i
    sig[p_i:] += p_amp * _wavelet(p_len, fs, freq=8.0, decay=1.5, rng=rng)

    # S arrival: larger, lower-frequency, slower decay (the destructive part).
    s_i = int(round(s_time * fs))
    s_len = n - s_i
    sig[s_i:] += s_amp * _wavelet(s_len, fs, freq=3.0, decay=0.6, rng=rng)

    meta = {
        "fs": fs,
        "p_time": p_time,
        "s_time": s_time,
        "warning_window": s_time - p_time,
    }
    return sig, meta
