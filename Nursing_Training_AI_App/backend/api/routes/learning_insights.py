"""
Learning Insights API — 8 endpoints under /api/learning/
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from core.continuous_learning import continuous_learning
from services.improvement_engine import improvement_engine
import services.learning_analytics as analytics

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.get("/dashboard", summary="Learning dashboard statistics")
async def dashboard() -> Dict[str, Any]:
    """High-level platform statistics: total evaluations, avg score, pass rate."""
    return analytics.get_dashboard_stats()


@router.get("/patterns", summary="Detected failure patterns")
async def patterns() -> List[Dict[str, Any]]:
    """Specialty+band combinations with >20% failure rate."""
    return analytics.get_failure_patterns()


@router.get("/trends", summary="Improving/stable/declining trends per specialty+band")
async def trends() -> Dict[str, str]:
    """Per-specialty+band trend analysis."""
    return analytics.get_trends()


@router.get("/proposals", summary="AI-generated improvement proposals")
async def proposals() -> List[Dict[str, Any]]:
    """Generate improvement proposals based on current failure patterns."""
    report = continuous_learning.run_cycle()
    weak = report.get("weak_areas", [])
    fp = analytics.get_failure_patterns()
    result = await improvement_engine.generate_proposals(weak, fp)
    return [
        {
            "priority": p.priority,
            "category": p.category,
            "description": p.description,
            "affected_specialty": p.affected_specialty,
            "affected_band": p.affected_band,
            "action_items": p.action_items,
        }
        for p in result
    ]


@router.get("/specialty/{specialty}", summary="Stats for a specific specialty")
async def specialty_stats(specialty: str) -> Dict[str, Any]:
    """Return aggregated stats filtered to a single specialty."""
    all_stats = analytics.get_specialty_band_stats()
    result = {k: v for k, v in all_stats.items() if k.startswith(specialty.lower())}
    if not result:
        raise HTTPException(status_code=404, detail=f"No data found for specialty '{specialty}'")
    return result


@router.get("/band/{band}", summary="Stats for a specific NHS band")
async def band_stats(band: str) -> Dict[str, Any]:
    """Return aggregated stats filtered to a single band."""
    all_stats = analytics.get_specialty_band_stats()
    result = {k: v for k, v in all_stats.items() if k.endswith(band.lower().replace(" ", "_"))}
    if not result:
        raise HTTPException(status_code=404, detail=f"No data found for band '{band}'")
    return result


@router.post("/run-cycle", summary="Trigger a full continuous learning cycle")
async def run_cycle() -> Dict[str, Any]:
    """Run the ML learning cycle: analyse outcomes, update weights, save report."""
    try:
        report = continuous_learning.run_cycle()
        return report
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/report/latest", summary="Retrieve the most recent learning report")
async def latest_report() -> Dict[str, Any]:
    """Return the most recently generated learning cycle report."""
    report = continuous_learning.latest_report()
    if report is None:
        raise HTTPException(status_code=404, detail="No learning reports available yet. POST /run-cycle first.")
    return report
