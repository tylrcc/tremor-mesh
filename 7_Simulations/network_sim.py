"""
Network-scale simulation: a quake hits a grid of nodes; does the mesh warn?

Stitches the whole system together in software, with no hardware and no
network:

    synthetic seismogram  ->  per-node STA/LTA detection (staggered by
    distance)  ->  consensus engine  ->  alert + warning lead time

It doubles as an integration test of the full pipeline. Run:

    python network_sim.py

The simulation logic lives in ``tremormesh/cli.py`` (``sim_main``).
"""

from __future__ import annotations

import os
import sys

# Allow running straight from a fresh clone (no install required).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tremormesh.cli import sim_main  # noqa: E402

if __name__ == "__main__":
    sys.exit(sim_main())
