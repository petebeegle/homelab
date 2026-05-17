#!/usr/bin/env python3
"""Safe, dev-gated blue/green workflow for Foundry VTT upgrades."""

from __future__ import annotations

import sys
from pathlib import Path


TOOLS_DIR = str(Path(__file__).resolve().parent)
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from foundry_bluegreen_pkg import main


if __name__ == "__main__":
    raise SystemExit(main())
