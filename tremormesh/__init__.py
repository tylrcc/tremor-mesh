"""TREMORMESH - open-source distributed earthquake early-warning mesh.

This package is the canonical, importable home of the core logic:

    * ``tremormesh.stalta``    - the recursive STA/LTA P-wave detector
    * ``tremormesh.synthetic`` - a synthetic seismogram generator
    * ``tremormesh.consensus`` - the quorum / geo-spread consensus engine

The numbered folders in the repository (``5_Algorithms/``, ``6_Server/`` …)
are the *guided tour*: runnable demos, tests, and narrative docs that import
from this package. Install it with ``pip install -e .`` and you also get the
``tremormesh-demo`` and ``tremormesh-sim`` console commands.
"""

from .consensus import Alert, ConsensusEngine, NodeTrigger
from .stalta import StaLtaConfig, Trigger, detect, recursive_sta_lta
from .synthetic import synthetic_seismogram

__version__ = "0.1.0"

__all__ = [
    "StaLtaConfig",
    "Trigger",
    "detect",
    "recursive_sta_lta",
    "synthetic_seismogram",
    "Alert",
    "ConsensusEngine",
    "NodeTrigger",
]
