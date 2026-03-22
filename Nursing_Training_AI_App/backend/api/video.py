from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Optional
from pydantic import BaseModel
from services.video_analysis_service import video_analysis_service
from core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/ai/video",
    tags=["video-analysis"],
    responses={404: {"description": "Not found"}},
)

class VideoAnalysisRequest(BaseModel):
    video_url: str
    context: Optional[str] = "Clinical Procedure"

@router.post("/analyze", summary="Analyze a clinical procedure video")
async def analyze_video(
    request: VideoAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a video using the newest AI models (Gemini 1.5 Pro / GPT-4o).
    """
    try:
        result = await video_analysis_service.analyze_clinical_procedure(
            video_path=request.video_url,
            context=request.context
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=result["message"]
            )
            
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video analysis failed: {str(e)}"
        )
