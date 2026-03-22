"""
Self-learning module: colectează rezultate, detectează tipare de eșec,
ajustează ponderi per specialitate și bandă, generează analize de trend.
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timezone
import json
import statistics

DIMENSIONS = [
    "knowledge_depth",
    "clinical_reasoning",
    "safety_awareness",
    "communication",
    "leadership",
]

DEFAULT_WEIGHTS = {f"{d}_weight": 1.0 for d in DIMENSIONS}

FAILURE_THRESHOLD = 60.0  # scor sub 60 = eșec
MIN_SAMPLES_FOR_PATTERN = 5  # minimum sesiuni pentru a detecta un tipar


class SelfLearning:
    def __init__(self, storage_dir: str = "models/self_learning") -> None:
        self.storage_path = Path(storage_dir)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.weights_file = self.storage_path / "weights.json"
        self.outcomes_file = self.storage_path / "outcomes.jsonl"
        if not self.weights_file.exists():
            self._save_weights({"_global": DEFAULT_WEIGHTS.copy()})

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _save_weights(self, weights: Dict[str, Any]) -> None:
        with open(self.weights_file, "w", encoding="utf-8") as f:
            json.dump(weights, f, indent=2)

    def _load_all_weights(self) -> Dict[str, Any]:
        with open(self.weights_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _key(self, specialty: str, band: str) -> str:
        return f"{specialty.lower()}:{band.lower()}"

    def _load_outcomes(self) -> List[Dict[str, Any]]:
        outcomes: List[Dict[str, Any]] = []
        if not self.outcomes_file.exists():
            return outcomes
        with open(self.outcomes_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    outcomes.append(json.loads(line))
                except Exception:
                    continue
        return outcomes

    # ------------------------------------------------------------------
    # Public API — backward-compatible signatures
    # ------------------------------------------------------------------

    def get_weights(self, specialty: Optional[str] = None, band: Optional[str] = None) -> Dict[str, float]:
        """Return dimension weights.

        If specialty and band are given, returns per-key weights (or falls back
        to global weights if no specific entry exists yet).
        Without arguments returns global weights — same as the original stub.
        """
        all_weights = self._load_all_weights()
        if specialty and band:
            key = self._key(specialty, band)
            return all_weights.get(key, all_weights.get("_global", DEFAULT_WEIGHTS.copy()))
        return all_weights.get("_global", DEFAULT_WEIGHTS.copy())

    def record_outcome(self, outcome: Dict[str, Any]) -> None:
        """Record a session outcome.

        Expected keys: band, specialty, overall_score, detailed_scores (optional),
        user_feedback_score (optional), question_id (optional), timestamp (auto-added).
        """
        outcome = dict(outcome)
        if "timestamp" not in outcome:
            outcome["timestamp"] = datetime.now(timezone.utc).isoformat()
        with open(self.outcomes_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(outcome) + "\n")

    def retrain(self, specialty: Optional[str] = None, band: Optional[str] = None) -> Dict[str, float]:
        """Recalculate and save weights based on recorded outcomes.

        If specialty + band are given, updates only that slice.
        Without arguments updates global weights — preserves original behaviour.
        """
        outcomes = self._load_outcomes()
        all_weights = self._load_all_weights()

        if specialty and band:
            key = self._key(specialty, band)
            filtered = [
                o for o in outcomes
                if o.get("specialty", "").lower() == specialty.lower()
                and o.get("band", "").lower() == band.lower()
            ]
            new_weights = self._compute_weights(filtered, all_weights.get(key, DEFAULT_WEIGHTS.copy()))
            all_weights[key] = new_weights
            self._save_weights(all_weights)
            return new_weights

        # Global update
        new_global = self._compute_weights(outcomes, all_weights.get("_global", DEFAULT_WEIGHTS.copy()))
        all_weights["_global"] = new_global
        self._save_weights(all_weights)
        return new_global

    # ------------------------------------------------------------------
    # New methods
    # ------------------------------------------------------------------

    def get_specialty_band_stats(
        self, specialty: Optional[str] = None, band: Optional[str] = None
    ) -> Dict[str, Any]:
        """Return aggregated statistics grouped by specialty+band (or filtered)."""
        outcomes = self._load_outcomes()
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for o in outcomes:
            sp = o.get("specialty", "unknown").lower()
            bd = o.get("band", "unknown").lower()
            if specialty and sp != specialty.lower():
                continue
            if band and bd != band.lower():
                continue
            key = f"{sp}:{bd}"
            groups.setdefault(key, []).append(o)

        stats: Dict[str, Any] = {}
        for key, records in groups.items():
            sp, bd = key.split(":", 1)
            scores = [float(r.get("overall_score", 0)) for r in records]
            dim_scores: Dict[str, List[float]] = {d: [] for d in DIMENSIONS}
            for r in records:
                detailed = r.get("detailed_scores", {})
                for d in DIMENSIONS:
                    if d in detailed:
                        dim_scores[d].append(float(detailed[d]))
            stats[key] = {
                "specialty": sp,
                "band": bd,
                "total_sessions": len(records),
                "avg_score": round(statistics.mean(scores), 2) if scores else 0.0,
                "min_score": round(min(scores), 2) if scores else 0.0,
                "max_score": round(max(scores), 2) if scores else 0.0,
                "pass_rate": round(
                    sum(1 for s in scores if s >= FAILURE_THRESHOLD) / len(scores) * 100, 2
                ) if scores else 0.0,
                "dimension_averages": {
                    d: round(statistics.mean(v), 2) if v else None
                    for d, v in dim_scores.items()
                },
            }
        return stats

    def get_failure_patterns(self) -> List[Dict[str, Any]]:
        """Detect failure patterns: specialty+band combinations with high failure rates."""
        stats = self.get_specialty_band_stats()
        patterns: List[Dict[str, Any]] = []
        for key, data in stats.items():
            if data["total_sessions"] < MIN_SAMPLES_FOR_PATTERN:
                continue
            failure_rate = 100.0 - data["pass_rate"]
            if failure_rate < 20.0:
                continue
            # Identify weakest dimension
            dim_avgs = {k: v for k, v in data["dimension_averages"].items() if v is not None}
            weakest_dim = min(dim_avgs, key=lambda d: dim_avgs[d]) if dim_avgs else None
            patterns.append({
                "specialty": data["specialty"],
                "band": data["band"],
                "failure_rate": round(failure_rate, 2),
                "avg_score": data["avg_score"],
                "total_sessions": data["total_sessions"],
                "weakest_dimension": weakest_dim,
                "weakest_dimension_avg": dim_avgs.get(weakest_dim) if weakest_dim else None,
                "description": (
                    f"{failure_rate:.0f}% fail in {data['specialty'].upper()} "
                    f"{data['band'].upper()} "
                    + (f"(weakest: {weakest_dim})" if weakest_dim else "")
                ),
            })
        patterns.sort(key=lambda p: p["failure_rate"], reverse=True)
        return patterns

    def get_trends(
        self, specialty: Optional[str] = None, band: Optional[str] = None, window: int = 10
    ) -> Dict[str, Any]:
        """Analyse score trends per specialty+band over the last `window` sessions."""
        outcomes = self._load_outcomes()
        # Group outcomes by specialty:band preserving insertion order (chronological)
        groups: Dict[str, List[float]] = {}
        for o in outcomes:
            sp = o.get("specialty", "unknown").lower()
            bd = o.get("band", "unknown").lower()
            if specialty and sp != specialty.lower():
                continue
            if band and bd != band.lower():
                continue
            key = f"{sp}:{bd}"
            groups.setdefault(key, []).append(float(o.get("overall_score", 0)))

        trends: Dict[str, Any] = {}
        for key, scores in groups.items():
            if len(scores) < 2:
                trends[key] = {"trend": "insufficient_data", "scores": scores}
                continue
            recent = scores[-window:]
            older = scores[: max(1, len(scores) - window)]
            recent_avg = statistics.mean(recent)
            older_avg = statistics.mean(older)
            delta = recent_avg - older_avg
            if abs(delta) < 2.0:
                trend_label = "stable"
            elif delta > 0:
                trend_label = "improving"
            else:
                trend_label = "declining"
            trends[key] = {
                "trend": trend_label,
                "recent_avg": round(recent_avg, 2),
                "older_avg": round(older_avg, 2),
                "delta": round(delta, 2),
                "total_sessions": len(scores),
                "recent_window": len(recent),
            }
        return trends

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _compute_weights(
        self, outcomes: List[Dict[str, Any]], current_weights: Dict[str, float]
    ) -> Dict[str, float]:
        """Compute updated dimension weights from a set of outcomes."""
        if not outcomes:
            return current_weights

        overall_scores = [float(o.get("overall_score", 0)) for o in outcomes]
        avg_overall = statistics.mean(overall_scores)

        new_weights = dict(current_weights)
        for dim in DIMENSIONS:
            dim_scores = [
                float(o["detailed_scores"][dim])
                for o in outcomes
                if isinstance(o.get("detailed_scores"), dict) and dim in o["detailed_scores"]
            ]
            weight_key = f"{dim}_weight"
            if not dim_scores:
                # Adjust only by overall average when no per-dimension data
                factor = 1.0 + (avg_overall - 75.0) / 500.0
                new_weights[weight_key] = round(
                    max(0.5, min(1.5, current_weights.get(weight_key, 1.0) * factor)), 4
                )
                continue
            dim_avg = statistics.mean(dim_scores)
            # Increase weight for weak dimensions (below threshold) so they get more focus
            if dim_avg < FAILURE_THRESHOLD:
                factor = 1.0 + (FAILURE_THRESHOLD - dim_avg) / 200.0
            else:
                factor = 1.0 + (dim_avg - 75.0) / 500.0
            new_weights[weight_key] = round(
                max(0.5, min(1.5, current_weights.get(weight_key, 1.0) * factor)), 4
            )
        return new_weights


self_learning = SelfLearning()
