"""
Learning Insights API Router
Provides endpoints for self-learning analytics, failure patterns,
AI-generated improvement proposals, and manual cycle triggers.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/learning", tags=["learning"])


def _get_continuous_learning():
    from core.continuous_learning import continuous_learning
    return continuous_learning


def _get_improvement_engine():
    from services.improvement_engine import improvement_engine
    return improvement_engine


def _get_analytics():
    from services.learning_analytics import learning_analytics_service
    return learning_analytics_service


def _get_self_learning():
    from core.self_learning import self_learning
    return self_learning


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/dashboard",
    summary="Overall learning analytics dashboard",
    response_description="Aggregated stats: total sessions, avg score, trends",
)
async def get_dashboard() -> Dict[str, Any]:
    """Return overall platform learning analytics."""
    try:
        return _get_analytics().get_dashboard()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


# ──────────────────────────────────────────────────────────────────────────────
# Failure patterns
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/patterns",
    summary="Detected failure patterns",
    response_description="Specialty+band combinations with high failure rates",
)
async def get_failure_patterns() -> List[Dict[str, Any]]:
    """Return all detected failure patterns across specialties and bands."""
    try:
        return _get_self_learning().get_failure_patterns()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


# ──────────────────────────────────────────────────────────────────────────────
# Trends
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/trends",
    summary="Score trends over time",
    response_description="Trend analysis per specialty+band (improving/stable/declining)",
)
async def get_trends() -> Dict[str, Any]:
    """Return score trends for all specialty+band combinations."""
    try:
        return _get_self_learning().get_trends()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


# ──────────────────────────────────────────────────────────────────────────────
# Improvement proposals
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/proposals",
    summary="AI-generated improvement proposals",
    response_description="List of ImprovementProposal objects with priority and action items",
)
async def get_proposals() -> List[Dict[str, Any]]:
    """Generate and return improvement proposals based on current failure patterns."""
    try:
        sl = _get_self_learning()
        cl = _get_continuous_learning()
        outcomes = cl.load_outcomes()
        groups = cl.group_by_specialty_band(outcomes)
        weak_areas = cl.identify_weak_areas(groups)
        failure_patterns = sl.get_failure_patterns()
        proposals = _get_improvement_engine().generate_proposals(failure_patterns, weak_areas)
        return [p.to_dict() for p in proposals]
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


# ──────────────────────────────────────────────────────────────────────────────
# Per-specialty
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/specialty/{specialty}",
    summary="Per-specialty analytics",
    response_description="Detailed analytics for the given specialty",
)
async def get_specialty_analytics(specialty: str) -> Dict[str, Any]:
    """Return detailed analytics for a specific specialty."""
    try:
        return _get_analytics().get_specialty_analytics(specialty)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


# ──────────────────────────────────────────────────────────────────────────────
# Per-band
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/band/{band}",
    summary="Per-band analytics",
    response_description="Detailed analytics for the given band",
)
async def get_band_analytics(band: str) -> Dict[str, Any]:
    """Return detailed analytics for a specific NHS band."""
    try:
        return _get_analytics().get_band_analytics(band)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


# ──────────────────────────────────────────────────────────────────────────────
# Trigger learning cycle (admin)
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/run-cycle",
    summary="Trigger a full learning cycle (admin only)",
    status_code=status.HTTP_200_OK,
    response_description="Learning cycle results including updated weights and detected patterns",
)
async def run_learning_cycle() -> Dict[str, Any]:
    """Run the full continuous learning cycle: analyse outcomes → update weights → save report."""
    try:
        return _get_continuous_learning().run_cycle()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


# ──────────────────────────────────────────────────────────────────────────────
# Latest report
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/report/latest",
    summary="Get latest learning report",
    response_description="Most recent learning cycle report in JSON format",
)
async def get_latest_report() -> Dict[str, Any]:
    """Return the most recently saved learning cycle report."""
    try:
        report = _get_continuous_learning().get_latest_report()
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No learning report found. Run /api/learning/run-cycle first.",
            )
        return report
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
