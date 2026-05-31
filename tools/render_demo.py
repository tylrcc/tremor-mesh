"""
Render the live-detection animation to demo.gif (and demo.mp4 via ffmpeg).

Frames are drawn from the *real* detector output, not a mock-up: it generates a
synthetic quake, runs the actual STA/LTA detector, and animates a cursor
sweeping the record while the traces reveal and the warning fires at the true
detection sample.

    python tools/render_demo.py

Outputs 8_Utils/demo.gif. If ffmpeg is on PATH it also writes demo.mp4.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tremormesh.stalta import StaLtaConfig, detect, recursive_sta_lta  # noqa: E402
from tremormesh.synthetic import synthetic_seismogram  # noqa: E402

W, H = 800, 450
X0, X1 = 70, 752
BG = (13, 19, 38)
PANEL = (35, 48, 77)
CYAN = (52, 211, 255)
RED = (255, 90, 77)
GREY = (91, 107, 140)
GREEN = (63, 185, 80)
TEXT = (230, 237, 247)
MUTED = (111, 134, 173)


def _font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except OSError:
                pass
    return ImageFont.load_default()


def main() -> None:
    cfg = StaLtaConfig()
    sig, meta = synthetic_seismogram(cfg.fs)
    ratio = recursive_sta_lta(sig, cfg)
    trigs = detect(sig, cfg)
    fs = cfg.fs
    dur = len(sig) / fs
    td = trigs[0].on_time
    lead = meta["s_time"] - td

    def xmap(t: float) -> float:
        return X0 + (t / dur) * (X1 - X0)

    # Precompute trace points at a stride for speed.
    stride = 4
    idx = list(range(0, len(sig), stride))
    times = [i / fs for i in idx]
    top = [(xmap(t), 158 - float(np.clip(sig[i], -1.4, 1.4)) * 58)
           for t, i in zip(times, idx)]
    bot = [(xmap(t), 420 - min(float(ratio[i]), 12.0) / 12.0 * 120)
           for t, i in zip(times, idx)]
    thr_y = 420 - min(cfg.thr_on, 12.0) / 12.0 * 120

    f_small = _font(13)
    f_lbl = _font(14, True)
    f_title = _font(20, True)
    f_alert = _font(18, True)
    f_alert2 = _font(13)

    n_sweep, n_hold = 64, 22
    frames = []
    for fi in range(n_sweep + n_hold):
        prog = min(fi / n_sweep, 1.0)
        cur_t = prog * dur
        k = max(2, int(prog * len(idx)))

        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        d.text((40, 18), "TREMORMESH", font=f_title, fill=TEXT)
        d.text((196, 22), "live detection  (synthetic quake)", font=f_small, fill=MUTED)

        # panel baselines / labels
        d.text((40, 70), "ground acceleration", font=f_small, fill=MUTED)
        d.line([(40, 158), (760, 158)], fill=PANEL, width=1)
        d.text((40, 300), "STA / LTA ratio", font=f_small, fill=MUTED)
        for x in range(40, 761, 6):  # dashed trigger threshold
            d.line([(x, thr_y), (x + 3, thr_y)], fill=GREY, width=1)
        d.text((628, thr_y - 18), "trigger threshold", font=f_small, fill=MUTED)

        # S-wave reference marker (faint, always shown)
        xs = xmap(meta["s_time"])
        for y in range(70, 430, 8):
            d.line([(xs, y), (xs, y + 4)], fill=(120, 60, 55), width=1)
        d.text((xs - 96, 60), "S-wave (damage)", font=f_small, fill=(190, 120, 110))

        # revealed traces
        d.line([p for p in top[:k]], fill=CYAN, width=2)
        d.line([p for p in bot[:k]], fill=RED, width=2)

        # sweeping cursor
        xc = xmap(cur_t)
        d.line([(xc, 60), (xc, 432)], fill=(255, 255, 255), width=1)

        # detection annotations once the cursor passes the true detection time
        if cur_t >= td:
            xd = xmap(td)
            for y in range(96, 420, 7):
                d.line([(xd, y), (xd, y + 3)], fill=GREEN, width=1)
            d.rectangle([xd - 6, 92, xd + 150, 118], fill=(17, 52, 29), outline=GREEN)
            d.text((xd + 4, 98), "P-WAVE DETECTED", font=f_lbl, fill=(95, 240, 138))

            flash = (fi // 3) % 2 == 0
            bcol = RED if flash else (150, 60, 52)
            d.rectangle([512, 250, 760, 312], fill=(58, 13, 10), outline=bcol, width=2)
            d.text((528, 260), "EARLY WARNING ISSUED", font=f_alert, fill=(255, 131, 119))
            d.text((528, 286), f"~{lead:.0f} s before strong shaking",
                   font=f_alert2, fill=(255, 210, 204))

        # consensus dots
        d.text((40, 424), "consensus:", font=f_small, fill=MUTED)
        for j in range(3):
            lit = cur_t >= td
            col = GREEN if lit else PANEL
            d.ellipse([124 + j * 22, 426, 136 + j * 22, 438], fill=col, outline=GREEN)
        d.text((196, 424), "3 separated nodes agree", font=f_small, fill=MUTED)

        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=128))

    out_gif = os.path.join(os.path.dirname(__file__), "..", "8_Utils", "demo.gif")
    out_gif = os.path.abspath(out_gif)
    frames[0].save(out_gif, save_all=True, append_images=frames[1:],
                   duration=70, loop=0, optimize=True, disposal=2)
    size_kb = os.path.getsize(out_gif) / 1024
    print(f"wrote {out_gif} ({size_kb:.0f} KB, {len(frames)} frames)")

    if shutil.which("ffmpeg"):
        out_mp4 = os.path.splitext(out_gif)[0] + ".mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-i", out_gif,
             "-movflags", "+faststart", "-pix_fmt", "yuv420p",
             "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", out_mp4],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"wrote {out_mp4} ({os.path.getsize(out_mp4) / 1024:.0f} KB)")
    else:
        print("ffmpeg not found; skipped mp4")


if __name__ == "__main__":
    main()
