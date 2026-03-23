#!/usr/bin/env python3
"""
Standalone cron script for the continuous learning cycle.

Usage:
    python scripts/run_learning_cycle.py

Designed to be executed periodically (e.g. daily via cron or a scheduled task).
The script:
1. Loads all recorded outcomes from outcomes.jsonl
2. Analyses weak areas and detects failure patterns
3. Generates improvement proposals (rule-based when Gemini unavailable)
4. Updates per-specialty × band weight slices
5. Saves a dated JSON report to models/self_learning/reports/
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

# Ensure the backend package root is on sys.path when running directly
_SCRIPT_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _SCRIPT_DIR.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from core.continuous_learning import ContinuousLearning  # noqa: E402
from core.self_learning import SelfLearning  # noqa: E402
from services.improvement_engine import ImprovementEngine  # noqa: E402


async def main() -> None:
    print("=== Nursing Training AI — Learning Cycle ===")

    cl = ContinuousLearning()
    sl = SelfLearning()
    engine = ImprovementEngine()

    # Step 1: Load outcomes
    outcomes = cl._load_outcomes()
    print(f"[1/5] Loaded {len(outcomes)} outcomes from {cl.outcomes_file}")

    # Step 2: Identify weak areas
    weak_areas = cl.identify_weak_areas(outcomes)
    print(f"[2/5] Identified {len(weak_areas)} weak area(s)")
    for area in weak_areas:
        print(f"      ↳ {area['specialty']} / {area['band']} — {area['dimension']} avg={area['avg_score']}%")

    # Step 3: Detect failure patterns
    failure_patterns = sl.get_failure_patterns()
    print(f"[3/5] Detected {len(failure_patterns)} failure pattern(s)")

    # Step 4: Generate improvement proposals
    proposals = await engine.generate_proposals(weak_areas, failure_patterns)
    print(f"[4/5] Generated {len(proposals)} improvement proposal(s)")
    for p in proposals:
        print(f"      [{p.priority.upper()}] {p.description}")

    # Step 5: Run full cycle (updates weights + saves report)
    report = cl.run_cycle()
    print(f"[5/5] Cycle complete — report saved to {report.get('report_path', 'N/A')}")
    print(f"      Weight slices updated: {report.get('weight_slices_updated', 0)}")
    print(f"      Global weights: {json.dumps(report.get('global_weights', {}), indent=2)}")

    print("\n✅ Learning cycle finished successfully.")


if __name__ == "__main__":
    asyncio.run(main())
