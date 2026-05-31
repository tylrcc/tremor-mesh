"""Make the ``tremormesh`` package importable during tests without an install.

pytest collects this file at the repo root and adds the root to ``sys.path``,
so ``import tremormesh`` works from a fresh clone. Installing the package with
``pip install -e .`` is still the recommended path for normal use.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
