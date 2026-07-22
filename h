#!/usr/bin/env python3
from pathlib import Path

from harness.cli import main


if __name__ == "__main__":
    raise SystemExit(main(root=Path(__file__).resolve().parent))
