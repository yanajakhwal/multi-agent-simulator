#!/usr/bin/env python3
"""Run the visualization dashboard."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dashboard.app import main

if __name__ == "__main__":
    main()

