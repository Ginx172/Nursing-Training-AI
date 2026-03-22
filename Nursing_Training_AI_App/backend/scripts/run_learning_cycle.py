#!/usr/bin/env python3
"""
Standalone learning cycle script — can be run via cron or CI.

Usage:
    python scripts/run_learning_cycle.py

Saves a report to models/self_learning/reports/report_YYYY-MM-DD.json
and prints a summary to stdout.
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timezone

# Allow imports from the backend package root
_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from core.continuous_learning import ContinuousLearning
from services.improvement_engine import ImprovementEngine


def main() -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting learning cycle...")

    cl = ContinuousLearning()
    ie = ImprovementEngine()

    # Step 1 — load outcomes
    outcomes = cl.load_outcomes()
    print(f"  Loaded {len(outcomes)} outcome records.")

    if not outcomes:
        print("  No outcomes found. Nothing to do.")
        return

    # Step 2 — run full cycle (analyse → update weights → save report)
    report = cl.run_cycle()

    # Step 3 — generate improvement proposals
    failure_patterns = report.get("failure_patterns", [])
    groups = cl.group_by_specialty_band(outcomes)
    weak_areas = cl.identify_weak_areas(groups)
    proposals = ie.generate_proposals(failure_patterns, weak_areas)

    # Attach proposals to report and re-save using ContinuousLearning's own method
    report["improvement_proposals"] = [p.to_dict() for p in proposals]
    cl._save_report(report)
    report_path = sorted(cl.reports_path.glob("report_*.json"), reverse=True)[0]

    # Step 4 — print summary
    summary = report.get("summary", {})
    print("\n=== LEARNING CYCLE SUMMARY ===")
    print(f"  Total outcomes analysed : {report.get('total_outcomes', 0)}")
    print(f"  Specialty+band groups   : {report.get('specialty_band_groups', 0)}")
    print(f"  Weak areas detected     : {summary.get('total_weak_areas', 0)}")
    print(f"  Failure patterns        : {summary.get('total_failure_patterns', 0)}")
    print(f"  Questions flagged       : {summary.get('questions_flagged', 0)}")
    print(f"  Proposals generated     : {len(proposals)}")
    print(f"  Report saved to         : {report_path}")
    print("==============================\n")

    if failure_patterns:
        print("Top failure patterns:")
        for p in failure_patterns[:5]:
            print(f"  - {p.get('description', '')}")

    if proposals:
        print("\nTop improvement proposals:")
        for prop in proposals[:5]:
            print(f"  [{prop.priority.upper()}] {prop.description}")


if __name__ == "__main__":
    main()
