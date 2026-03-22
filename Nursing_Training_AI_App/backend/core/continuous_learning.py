"""
Continuous Learning Engine — analizează outcomes, identifică lacune,
propune îmbunătățiri și actualizează ponderi.
"""

from __future__ import annotations

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .self_learning import SelfLearning, DIMENSIONS, FAILURE_THRESHOLD

WEAK_AREA_THRESHOLD = 60.0  # avg dimension score below this → weak area
HIGH_DIFFICULTY_THRESHOLD = 40.0  # if everyone scores < 40 → question too hard
LOW_DIFFICULTY_THRESHOLD = 95.0  # if everyone scores > 95 → question too easy


class ContinuousLearning:
    """ML engine for continuous learning cycle."""

    def __init__(self, storage_dir: str = "models/self_learning") -> None:
        self.storage_path = Path(storage_dir)
        self.reports_path = self.storage_path / "reports"
        self.reports_path.mkdir(parents=True, exist_ok=True)
        self.self_learning = SelfLearning(storage_dir=storage_dir)

    # ------------------------------------------------------------------
    # Core analysis
    # ------------------------------------------------------------------

    def load_outcomes(self) -> List[Dict[str, Any]]:
        outcomes_file = self.storage_path / "outcomes.jsonl"
        if not outcomes_file.exists():
            return []
        outcomes: List[Dict[str, Any]] = []
        with open(outcomes_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    outcomes.append(json.loads(line))
                except Exception:
                    continue
        return outcomes

    def group_by_specialty_band(
        self, outcomes: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for o in outcomes:
            sp = o.get("specialty", "unknown").lower()
            bd = o.get("band", "unknown").lower()
            key = f"{sp}:{bd}"
            groups.setdefault(key, []).append(o)
        return groups

    def identify_weak_areas(
        self, groups: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Find specialty+band+dimension combinations with avg score < threshold."""
        weak: List[Dict[str, Any]] = []
        for key, records in groups.items():
            sp, bd = key.split(":", 1)
            for dim in DIMENSIONS:
                scores = [
                    float(r["detailed_scores"][dim])
                    for r in records
                    if isinstance(r.get("detailed_scores"), dict)
                    and dim in r["detailed_scores"]
                ]
                if not scores:
                    continue
                avg = statistics.mean(scores)
                if avg < WEAK_AREA_THRESHOLD:
                    weak.append({
                        "specialty": sp,
                        "band": bd,
                        "dimension": dim,
                        "avg_score": round(avg, 2),
                        "sample_size": len(scores),
                        "severity": "critical" if avg < 40 else "high" if avg < 50 else "medium",
                    })
        weak.sort(key=lambda x: x["avg_score"])
        return weak

    def calibrate_question_difficulty(
        self, outcomes: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Flag questions that are too hard or too easy based on overall scores."""
        q_scores: Dict[str, List[float]] = {}
        for o in outcomes:
            qid = str(o.get("question_id", ""))
            if not qid:
                continue
            q_scores.setdefault(qid, []).append(float(o.get("overall_score", 0)))

        calibration: Dict[str, Dict[str, Any]] = {}
        for qid, scores in q_scores.items():
            avg = statistics.mean(scores)
            flag = "normal"
            if avg < HIGH_DIFFICULTY_THRESHOLD:
                flag = "too_hard"
            elif avg > LOW_DIFFICULTY_THRESHOLD:
                flag = "too_easy"
            calibration[qid] = {
                "avg_score": round(avg, 2),
                "sample_size": len(scores),
                "flag": flag,
            }
        return calibration

    # ------------------------------------------------------------------
    # Full learning cycle
    # ------------------------------------------------------------------

    def run_cycle(self) -> Dict[str, Any]:
        """Full cycle: load → analyse → detect gaps → update weights → save report."""
        outcomes = self.load_outcomes()
        groups = self.group_by_specialty_band(outcomes)

        # Update weights per specialty+band
        updated_keys: List[str] = []
        for key in groups:
            sp, bd = key.split(":", 1)
            self.self_learning.retrain(specialty=sp, band=bd)
            updated_keys.append(key)
        # Also update global weights
        self.self_learning.retrain()

        weak_areas = self.identify_weak_areas(groups)
        failure_patterns = self.self_learning.get_failure_patterns()
        trends = self.self_learning.get_trends()
        difficulty_calibration = self.calibrate_question_difficulty(outcomes)

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_outcomes": len(outcomes),
            "specialty_band_groups": len(groups),
            "updated_weight_keys": updated_keys,
            "weak_areas": weak_areas,
            "failure_patterns": failure_patterns,
            "trends": trends,
            "difficulty_calibration": difficulty_calibration,
            "summary": {
                "total_weak_areas": len(weak_areas),
                "total_failure_patterns": len(failure_patterns),
                "questions_flagged": sum(
                    1 for v in difficulty_calibration.values() if v["flag"] != "normal"
                ),
            },
        }

        self._save_report(report)
        return report

    def _save_report(self, report: Dict[str, Any]) -> None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        report_file = self.reports_path / f"report_{date_str}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        reports = sorted(self.reports_path.glob("report_*.json"), reverse=True)
        if not reports:
            return None
        with open(reports[0], "r", encoding="utf-8") as f:
            return json.load(f)


continuous_learning = ContinuousLearning()
