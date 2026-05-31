"""
End-to-end demo: fabricate a quake, detect the P-wave, report the warning.

Run:
    python demo.py            # text report
    python demo.py --plot     # also save stalta_demo.png (needs matplotlib)

This is the fastest way to *see* TREMORMESH work without any hardware. The
detection logic lives in ``tremormesh/stalta.py``; this script just drives it.
"""

from __future__ import annotations

import os
import sys

# Allow running straight from a fresh clone (no install required).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tremormesh.cli import demo_main  # noqa: E402

if __name__ == "__main__":
    demo_main()
