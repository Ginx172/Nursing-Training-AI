#!/usr/bin/env python
"""
Standalone script for cron-scheduled continuous learning cycles.

Usage:
    python scripts/run_learning_cycle.py [--storage-dir <path>] [--reports-dir <path>]

Environment variables honoured:
    SELF_LEARNING_STORAGE_DIR   (default: models/self_learning)
    LEARNING_REPORTS_DIR        (default: models/reports)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a continuous learning cycle.")
    parser.add_argument(
        "--storage-dir",
        default=os.getenv("SELF_LEARNING_STORAGE_DIR", "models/self_learning"),
        help="Directory for self-learning weights and outcomes.",
    )
    parser.add_argument(
        "--reports-dir",
        default=os.getenv("LEARNING_REPORTS_DIR", "models/reports"),
        help="Directory where JSON reports are saved.",
    )
    args = parser.parse_args()

    # Ensure the backend package is importable when run from the repo root
    backend_dir = Path(__file__).resolve().parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    from core.continuous_learning import ContinuousLearning  # noqa: E402

    print(f"[run_learning_cycle] Starting cycle …")
    print(f"  storage_dir : {args.storage_dir}")
    print(f"  reports_dir : {args.reports_dir}")

    cl = ContinuousLearning(
        storage_dir=args.storage_dir,
        reports_dir=args.reports_dir,
    )
    report = cl.run_cycle()

    print(f"[run_learning_cycle] Cycle complete.")
    print(f"  outcomes processed : {report['outcomes_processed']}")
    print(f"  weak areas found   : {len(report['weak_areas'])}")
    print(f"  question flags     : {len(report['question_flags'])}")
    print()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
