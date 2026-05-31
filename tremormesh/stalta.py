"""
Recursive STA/LTA P-wave trigger detector, the reference implementation.

The STA/LTA (Short-Term Average / Long-Term Average) ratio is the classic
seismic trigger. We compute a *characteristic function* from the incoming
acceleration stream (here: the squared, mean-removed signal, i.e. its
instantaneous energy), then track two exponential moving averages of it:

    * STA: a short window (~0.5 s) that reacts quickly to new energy
    * LTA: a long window  (~10 s) that represents the ambient noise floor

When ground motion arrives, the STA rises far faster than the LTA, so the
ratio STA/LTA spikes. A trigger is declared when the ratio crosses an
``on`` threshold and is released when it falls back below an ``off``
threshold (hysteresis prevents chattering).

This recursive (single-pass, O(1) memory) form is deliberately chosen
because it is *exactly* what the ESP32 firmware in ``4_Firmware/node`` runs
in fixed time per sample. This file is the human-readable ground truth used
to validate the embedded port. See ``5_Algorithms/test_stalta.py``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class StaLtaConfig:
    """Detector configuration.

    Attributes:
        fs:        Sample rate of the accelerometer stream, in Hz.
        sta_sec:   Short-term average window length, in seconds.
        lta_sec:   Long-term average window length, in seconds.
        thr_on:    STA/LTA ratio at which a trigger turns ON.
        thr_off:   STA/LTA ratio at which an active trigger turns OFF.
    """

    fs: float = 100.0
    sta_sec: float = 0.5
    lta_sec: float = 10.0
    thr_on: float = 4.0
    thr_off: float = 1.5

    @property
    def nsta(self) -> int:
        return max(1, int(round(self.sta_sec * self.fs)))

    @property
    def nlta(self) -> int:
        return max(1, int(round(self.lta_sec * self.fs)))


@dataclass
class Trigger:
    """A single detected event, in sample indices and seconds."""

    on_index: int
    off_index: int
    fs: float
    peak_ratio: float

    @property
    def on_time(self) -> float:
        return self.on_index / self.fs

    @property
    def off_time(self) -> float:
        return self.off_index / self.fs


def recursive_sta_lta(x: np.ndarray, cfg: StaLtaConfig) -> np.ndarray:
    """Return the per-sample STA/LTA ratio for an acceleration stream.

    The first ``nlta`` samples are a warm-up region where the LTA has not
    yet stabilised; the returned ratio there is clamped to a neutral value
    so it cannot produce a spurious trigger.
    """
    x = np.asarray(x, dtype=float)
    if x.ndim != 1:
        raise ValueError("x must be a 1-D acceleration stream")

    cf = (x - float(np.mean(x))) ** 2  # characteristic function: energy

    csta = 1.0 / cfg.nsta
    clta = 1.0 / cfg.nlta

    sta = 0.0
    # Seed the LTA with the first sample's energy so the very first ratios
    # are ~1.0 rather than exploding through a division by zero.
    lta = float(cf[0]) if cf.size else 0.0
    eps = 1e-12

    ratio = np.ones_like(cf)
    for i in range(cf.size):
        sta += csta * (cf[i] - sta)
        lta += clta * (cf[i] - lta)
        ratio[i] = sta / lta if lta > eps else 1.0

    # Suppress the warm-up transient.
    ratio[: cfg.nlta] = 1.0
    return ratio


def detect(x: np.ndarray, cfg: StaLtaConfig | None = None) -> list[Trigger]:
    """Run the full trigger state machine over a stream and return events."""
    cfg = cfg or StaLtaConfig()
    ratio = recursive_sta_lta(x, cfg)

    triggers: list[Trigger] = []
    active = False
    on_idx = 0
    peak = 0.0

    for i, r in enumerate(ratio):
        if not active and r >= cfg.thr_on:
            active = True
            on_idx = i
            peak = r
        elif active:
            peak = max(peak, r)
            if r <= cfg.thr_off:
                triggers.append(Trigger(on_idx, i, cfg.fs, peak))
                active = False

    if active:  # event still open at end of stream
        triggers.append(Trigger(on_idx, len(ratio) - 1, cfg.fs, peak))
    return triggers
