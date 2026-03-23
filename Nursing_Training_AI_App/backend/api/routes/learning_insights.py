"""
Learning Insights API – 8 endpoints under /api/learning/
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from core.continuous_learning import continuous_learning
from core.self_learning import self_learning
from services.improvement_engine import improvement_engine
from services.learning_analytics import learning_analytics

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.get("/dashboard", summary="Learning dashboard KPIs")
async def get_dashboard() -> Dict[str, Any]:
    """Return high-level learning KPIs."""
    return learning_analytics.get_dashboard_stats()


@router.get("/patterns", summary="Failure patterns per specialty×band×dimension")
async def get_patterns() -> List[Dict[str, Any]]:
    """Return combinations with >20 % failure rate."""
    return self_learning.get_failure_patterns()


@router.get("/trends", summary="Improving/stable/declining trends")
async def get_trends() -> List[Dict[str, Any]]:
    """Return score trends per specialty+band."""
    return self_learning.get_trends()


@router.get("/proposals", summary="AI-powered improvement proposals")
async def get_proposals() -> List[Dict[str, Any]]:
    """Generate improvement proposals for the current weak areas."""
    weak_areas = self_learning.get_failure_patterns()
    proposals = await improvement_engine.generate_proposals(weak_areas)
    return [
        {
            "specialty": p.specialty,
            "band": p.band,
            "dimension": p.dimension,
            "title": p.title,
            "description": p.description,
            "actions": p.actions,
            "priority": p.priority,
            "source": p.source,
        }
        for p in proposals
    ]


@router.get("/specialty", summary="Specialty heatmap data")
async def get_specialty_heatmap() -> List[Dict[str, Any]]:
    """Return avg scores per specialty × dimension."""
    return learning_analytics.get_specialty_heatmap()


@router.get("/band", summary="Band progression data")
async def get_band_progression() -> List[Dict[str, Any]]:
    """Return avg overall score per band."""
    return learning_analytics.get_band_progression()


@router.post("/run-cycle", summary="Trigger a learning cycle")
async def run_learning_cycle() -> Dict[str, Any]:
    """Execute a full continuous-learning cycle and return the report."""
    try:
        report = continuous_learning.run_cycle()
        return report
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/report/latest", summary="Latest learning cycle report")
async def get_latest_report() -> Dict[str, Any]:
    """Return the most recent saved learning cycle report."""
    report = continuous_learning.get_latest_report()
    if report is None:
        raise HTTPException(status_code=404, detail="No reports found. Run a cycle first.")
    return report
