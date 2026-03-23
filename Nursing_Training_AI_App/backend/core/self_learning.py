"""
Self-learning module: colectează rezultate, antrenează un model simplu (stub), ajustează ponderi.
Suportă ponderi per specialitate × band cu 5 dimensiuni:
knowledge_depth, clinical_reasoning, safety_awareness, communication, leadership.
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json
from collections import defaultdict

DIMENSIONS = ["knowledge_depth", "clinical_reasoning", "safety_awareness", "communication", "leadership"]

_DEFAULT_WEIGHTS = {dim: 1.0 for dim in DIMENSIONS}


class SelfLearning:
    def __init__(self, storage_dir: str = "models/self_learning") -> None:
        self.storage_path = Path(storage_dir)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.weights_file = self.storage_path / "weights.json"
        self.outcomes_file = self.storage_path / "outcomes.jsonl"
        if not self.weights_file.exists():
            self._save_weights({"global": dict(_DEFAULT_WEIGHTS)})

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _save_weights(self, weights: Dict[str, Any]) -> None:
        with open(self.weights_file, "w", encoding="utf-8") as f:
            json.dump(weights, f, indent=2)

    def _load_all_weights(self) -> Dict[str, Any]:
        with open(self.weights_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _slice_key(self, specialty: Optional[str], band: Optional[str]) -> str:
        """Return a canonical key for a specialty+band combination."""
        s = (specialty or "general").lower().replace(" ", "_")
        b = (band or "band_5").lower().replace(" ", "_")
        return f"{s}__{b}"

    def _read_outcomes(self) -> List[Dict[str, Any]]:
        outcomes: List[Dict[str, Any]] = []
        if not self.outcomes_file.exists():
            return outcomes
        with open(self.outcomes_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    outcomes.append(json.loads(line))
                except Exception:
                    continue
        return outcomes

    # ------------------------------------------------------------------ #
    # Public API (backward-compatible)                                     #
    # ------------------------------------------------------------------ #

    def get_weights(self, specialty: Optional[str] = None, band: Optional[str] = None) -> Dict[str, float]:
        """Return weights for a given specialty+band slice, falling back to global."""
        all_weights = self._load_all_weights()
        if specialty or band:
            key = self._slice_key(specialty, band)
            return all_weights.get(key, all_weights.get("global", dict(_DEFAULT_WEIGHTS)))
        return all_weights.get("global", dict(_DEFAULT_WEIGHTS))

    def record_outcome(self, outcome: Dict[str, Any]) -> None:
        """Record an evaluation outcome.

        Expected keys: band, specialty, overall_score, user_feedback_score,
        detailed_scores (optional dict of dimension → score).
        """
        with open(self.outcomes_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(outcome) + "\n")

    def retrain(self) -> Dict[str, float]:
        """Re-calculate per-specialty×band weights from all recorded outcomes.
        Returns the updated global weights dict for backward compatibility.
        """
        outcomes = self._read_outcomes()
        if not outcomes:
            return self.get_weights()

        # Group outcomes by slice key
        groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for o in outcomes:
            key = self._slice_key(o.get("specialty"), o.get("band"))
            groups[key].append(o)

        all_weights = self._load_all_weights()

        # Update per-slice weights
        global_totals: Dict[str, List[float]] = defaultdict(list)
        for key, records in groups.items():
            slice_weights = dict(_DEFAULT_WEIGHTS)
            for dim in DIMENSIONS:
                scores = [
                    r.get("detailed_scores", {}).get(dim, r.get("overall_score", 75.0))
                    for r in records
                ]
                if scores:
                    avg = sum(scores) / len(scores)
                    # Weights shift toward 1.5 for weak areas, 0.5 for strong
                    factor = 1.0 + (75.0 - avg) / 250.0
                    slice_weights[dim] = max(0.5, min(1.5, factor))
                    global_totals[dim].extend(scores)
            all_weights[key] = slice_weights

        # Update global weights
        global_weights = {}
        for dim in DIMENSIONS:
            if global_totals[dim]:
                avg = sum(global_totals[dim]) / len(global_totals[dim])
                factor = 1.0 + (75.0 - avg) / 250.0
                global_weights[dim] = max(0.5, min(1.5, factor))
            else:
                global_weights[dim] = _DEFAULT_WEIGHTS[dim]
        all_weights["global"] = global_weights

        self._save_weights(all_weights)
        return global_weights

    # ------------------------------------------------------------------ #
    # Analytics helpers                                                    #
    # ------------------------------------------------------------------ #

    def get_specialty_band_stats(self) -> Dict[str, Any]:
        """Return aggregated stats per specialty+band."""
        outcomes = self._read_outcomes()
        groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for o in outcomes:
            key = self._slice_key(o.get("specialty"), o.get("band"))
            groups[key].append(o)

        stats: Dict[str, Any] = {}
        for key, records in groups.items():
            overall_scores = [r.get("overall_score", 0.0) for r in records]
            dim_avgs: Dict[str, float] = {}
            for dim in DIMENSIONS:
                vals = [r.get("detailed_scores", {}).get(dim) for r in records if r.get("detailed_scores", {}).get(dim) is not None]
                dim_avgs[dim] = round(sum(vals) / len(vals), 2) if vals else 0.0
            stats[key] = {
                "count": len(records),
                "avg_score": round(sum(overall_scores) / len(overall_scores), 2),
                "pass_rate": round(sum(1 for s in overall_scores if s >= 60) / len(overall_scores) * 100, 2),
                "dimension_averages": dim_avgs,
            }
        return stats

    def get_failure_patterns(self, failure_threshold: float = 20.0) -> List[Dict[str, Any]]:
        """Detect specialty+band+dimension combos with >failure_threshold% failure rate."""
        stats = self.get_specialty_band_stats()
        patterns: List[Dict[str, Any]] = []
        for key, data in stats.items():
            failure_rate = 100.0 - data["pass_rate"]
            if failure_rate > failure_threshold:
                specialty, band = (key.split("__") + ["unknown"])[:2]
                weak_dims = [
                    dim for dim, avg in data["dimension_averages"].items()
                    if avg < 60
                ]
                patterns.append({
                    "specialty": specialty,
                    "band": band,
                    "failure_rate": round(failure_rate, 2),
                    "sample_count": data["count"],
                    "weak_dimensions": weak_dims,
                })
        patterns.sort(key=lambda x: x["failure_rate"], reverse=True)
        return patterns

    def get_trends(self, window: int = 10) -> Dict[str, str]:
        """Return improving/stable/declining trend per specialty+band.
        Compares the last *window* outcomes against the prior *window*.
        """
        outcomes = self._read_outcomes()
        groups: Dict[str, List[float]] = defaultdict(list)
        for o in outcomes:
            key = self._slice_key(o.get("specialty"), o.get("band"))
            groups[key].append(o.get("overall_score", 0.0))

        trends: Dict[str, str] = {}
        for key, scores in groups.items():
            if len(scores) < 2:
                trends[key] = "stable"
                continue
            recent = scores[-window:]
            prior = scores[-2 * window:-window] if len(scores) >= 2 * window else scores[:-window]
            if not prior:
                trends[key] = "stable"
                continue
            avg_recent = sum(recent) / len(recent)
            avg_prior = sum(prior) / len(prior)
            diff = avg_recent - avg_prior
            if diff > 2.0:
                trends[key] = "improving"
            elif diff < -2.0:
                trends[key] = "declining"
            else:
                trends[key] = "stable"
        return trends


self_learning = SelfLearning()


