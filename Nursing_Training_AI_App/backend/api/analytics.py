"""
Analytics API Endpoints
Provides analytics data for users, admins, and platform metrics
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from services.analytics_service import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Response Models
class UserAnalyticsResponse(BaseModel):
    success: bool
    analytics: dict

class PlatformMetricsResponse(BaseModel):
    success: bool
    metrics: dict

# USER ANALYTICS ENDPOINTS

@router.get("/user/{user_id}")
async def get_user_analytics(
    user_id: str,
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    """Get comprehensive analytics for a user"""
    try:
        # Parse dates
        from_date = datetime.fromisoformat(date_from) if date_from else None
        to_date = datetime.fromisoformat(date_to) if date_to else None
        
        analytics = analytics_service.get_user_analytics(user_id, from_date, to_date)
        
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}/progress")
async def get_user_progress(user_id: str, current_band: str):
    """Get user progress to next band"""
    try:
        progress = analytics_service.get_user_progress_to_next_band(user_id, current_band)
        
        return {
            "success": True,
            "progress": progress
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}/weekly-summary")
async def get_weekly_summary(user_id: str):
    """Get weekly summary for user"""
    try:
        summary = analytics_service.generate_weekly_summary(user_id)
        
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}/export")
async def export_user_report(
    user_id: str,
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    format: str = Query("json", regex="^(json|pdf|excel)$")
):
    """Export user report in specified format"""
    try:
        from_date = datetime.fromisoformat(date_from) if date_from else datetime.now() - timedelta(days=30)
        to_date = datetime.fromisoformat(date_to) if date_to else datetime.now()
        
        export_data = analytics_service.export_user_report_data(user_id, from_date, to_date)
        
        if format == "json":
            return {"success": True, "data": export_data}
        
        elif format == "pdf":
            # TODO: Generate PDF report
            return {"success": True, "message": "PDF generation not implemented yet"}
        
        elif format == "excel":
            # TODO: Generate Excel report
            return {"success": True, "message": "Excel generation not implemented yet"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# CONTENT ANALYTICS ENDPOINTS

@router.get("/questions/{question_id}")
async def get_question_analytics(question_id: str):
    """Get analytics for a specific question"""
    try:
        analytics = analytics_service.get_question_analytics(question_id)
        
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/question-bank/{sector}/{specialty}/{band}")
async def get_question_bank_analytics(
    sector: str,
    specialty: str,
    band: str
):
    """Get analytics for a question bank"""
    try:
        analytics = analytics_service.get_question_bank_analytics(sector, specialty, band)
        
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/content/effectiveness")
async def get_content_effectiveness():
    """Get content effectiveness analysis"""
    try:
        analysis = analytics_service.analyze_content_effectiveness()
        
        return {
            "success": True,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# PLATFORM ANALYTICS ENDPOINTS (Admin only)

@router.get("/platform/metrics")
async def get_platform_metrics(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    """Get platform-wide metrics (Admin only)"""
    try:
        # TODO: Add authentication check for admin
        from_date = datetime.fromisoformat(date_from) if date_from else datetime.now() - timedelta(days=30)
        to_date = datetime.fromisoformat(date_to) if date_to else datetime.now()
        
        metrics = analytics_service.get_platform_metrics(from_date, to_date)
        
        return {
            "success": True,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/platform/realtime")
async def get_realtime_metrics():
    """Get real-time platform metrics (Admin only)"""
    try:
        # TODO: Add authentication check for admin
        metrics = analytics_service.get_realtime_metrics()
        
        return {
            "success": True,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/platform/cohorts")
async def get_cohort_analysis(cohort_type: str = "monthly"):
    """Get cohort analysis (Admin only)"""
    try:
        # TODO: Add authentication check for admin
        cohorts = analytics_service.get_cohort_analysis(cohort_type)
        
        return {
            "success": True,
            "cohorts": cohorts
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# LEADERBOARD ENDPOINTS

@router.get("/leaderboard")
async def get_leaderboard(
    scope: str = Query("global"),
    specialty: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    band: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100)
):
    """Get leaderboard"""
    try:
        filter_by = {}
        if specialty:
            filter_by["specialty"] = specialty
        if sector:
            filter_by["sector"] = sector
        if band:
            filter_by["band"] = band
        
        leaderboard = analytics_service.get_leaderboard(
            scope=scope,
            filter_by=filter_by if filter_by else None,
            limit=limit
        )
        
        return {
            "success": True,
            "leaderboard": leaderboard,
            "scope": scope,
            "filter": filter_by
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# TEAM ANALYTICS ENDPOINTS (Enterprise only)

@router.get("/team/{organization_id}")
async def get_team_analytics(
    organization_id: str,
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    """Get team analytics for organization (Enterprise only)"""
    try:
        # TODO: Verify user has Enterprise plan
        from_date = datetime.fromisoformat(date_from) if date_from else datetime.now() - timedelta(days=30)
        to_date = datetime.fromisoformat(date_to) if date_to else datetime.now()
        
        analytics = analytics_service.get_team_analytics(organization_id, from_date, to_date)
        
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

