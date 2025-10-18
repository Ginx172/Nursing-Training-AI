"""
🤖 AI Services API Routes
Endpoint-uri pentru serviciile AI (RAG, MCP, Knowledge Base)
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from services.rag_service import rag_service, RAGQuery, SearchResult
from services.mcp_service import mcp_service, MCPRequest, MCPResponse, ContextType
from services.knowledge_base_service import knowledge_base_service, DocumentInfo
from services.ai_integration_service import ai_integration_service, AIEvaluationRequest, AIEvaluationResponse
from core.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================================================
# RAG Service Endpoints
# ============================================================================

class RAGSearchRequest(BaseModel):
    query: str
    specialty: str
    band: str
    max_results: int = 5
    min_score: float = 0.7

class RAGSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_found: int
    query: str
    specialty: str

@router.post("/rag/search", response_model=RAGSearchResponse)
async def search_rag(request: RAGSearchRequest, current_user: dict = Depends(get_current_user)):
    """Caută în Knowledge Base folosind RAG"""
    try:
        # Creează query RAG
        rag_query = RAGQuery(
            query_text=request.query,
            specialty=request.specialty,
            band=request.band,
            max_results=request.max_results,
            min_score=request.min_score
        )
        
        # Caută
        results = await rag_service.search(rag_query)
        
        # Convertește rezultatele
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result.content,
                "source": result.source,
                "score": result.score,
                "metadata": result.metadata,
                "chunk_id": result.chunk_id
            })
        
        return RAGSearchResponse(
            results=formatted_results,
            total_found=len(formatted_results),
            query=request.query,
            specialty=request.specialty
        )
        
    except Exception as e:
        logger.error(f"❌ Error in RAG search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG search error: {str(e)}")

@router.get("/rag/context/{specialty}/{band}")
async def get_rag_context(question: str, specialty: str, band: str, current_user: dict = Depends(get_current_user)):
    """Obține context RAG pentru o întrebare"""
    try:
        context = await rag_service.get_context_for_question(question, specialty, band)
        
        return {
            "context": context,
            "question": question,
            "specialty": specialty,
            "band": band
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting RAG context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG context error: {str(e)}")

@router.get("/rag/recommendations/{specialty}/{band}")
async def get_rag_recommendations(question: str, specialty: str, band: str, current_user: dict = Depends(get_current_user)):
    """Obține recomandări de studiu din RAG"""
    try:
        recommendations = await rag_service.get_recommendations(question, specialty, band)
        
        return {
            "recommendations": recommendations,
            "question": question,
            "specialty": specialty,
            "band": band
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting RAG recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG recommendations error: {str(e)}")

# ============================================================================
# MCP Service Endpoints
# ============================================================================

class MCPRequestModel(BaseModel):
    query: str
    context_type: str
    specialty: str
    band: str
    user_data: Optional[Dict[str, Any]] = None
    additional_context: Optional[str] = None

@router.post("/mcp/process", response_model=Dict[str, Any])
async def process_mcp_request(request: MCPRequestModel, current_user: dict = Depends(get_current_user)):
    """Procesează un request MCP"""
    try:
        # Convertește context_type
        try:
            context_type = ContextType(request.context_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid context_type: {request.context_type}")
        
        # Creează request MCP
        mcp_request = MCPRequest(
            query=request.query,
            context_type=context_type,
            specialty=request.specialty,
            band=request.band,
            user_data=request.user_data,
            additional_context=request.additional_context
        )
        
        # Procesează
        response = await mcp_service.process_request(mcp_request)
        
        return {
            "response": response.response,
            "model_used": response.model_used,
            "confidence": response.confidence,
            "context_used": response.context_used,
            "metadata": response.metadata
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing MCP request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"MCP processing error: {str(e)}")

# ============================================================================
# Knowledge Base Service Endpoints
# ============================================================================

class KBSearchRequest(BaseModel):
    query: str
    specialty: str
    band: Optional[str] = None

@router.post("/knowledge-base/search", response_model=List[Dict[str, Any]])
async def search_knowledge_base(request: KBSearchRequest, current_user: dict = Depends(get_current_user)):
    """Caută în Knowledge Base"""
    try:
        results = await knowledge_base_service.search_documents(
            query=request.query,
            specialty=request.specialty,
            band=request.band
        )
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "document": {
                    "title": result.document.title,
                    "specialty": result.document.specialty,
                    "band": result.document.band,
                    "file_path": result.document.file_path,
                    "file_type": result.document.file_type,
                    "size": result.document.size,
                    "last_modified": result.document.last_modified.isoformat()
                },
                "relevance_score": result.relevance_score,
                "matched_content": result.matched_content,
                "page_number": result.page_number
            })
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"❌ Error searching Knowledge Base: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Knowledge Base search error: {str(e)}")

@router.get("/knowledge-base/specialties")
async def get_available_specialties(current_user: dict = Depends(get_current_user)):
    """Obține lista specialităților disponibile"""
    try:
        specialties = await knowledge_base_service.get_available_specialties()
        return {"specialties": specialties}
        
    except Exception as e:
        logger.error(f"❌ Error getting specialties: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting specialties: {str(e)}")

@router.get("/knowledge-base/bands")
async def get_available_bands(current_user: dict = Depends(get_current_user)):
    """Obține lista band-urilor disponibile"""
    try:
        bands = await knowledge_base_service.get_available_bands()
        return {"bands": bands}
        
    except Exception as e:
        logger.error(f"❌ Error getting bands: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting bands: {str(e)}")

@router.get("/knowledge-base/specialty/{specialty}")
async def get_specialty_documents(specialty: str, band: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Obține documentele pentru o specialitate"""
    try:
        documents = await knowledge_base_service.get_specialty_documents(specialty, band)
        
        formatted_docs = []
        for doc in documents:
            formatted_docs.append({
                "title": doc.title,
                "specialty": doc.specialty,
                "band": doc.band,
                "file_path": doc.file_path,
                "file_type": doc.file_type,
                "size": doc.size,
                "last_modified": doc.last_modified.isoformat(),
                "indexed": doc.indexed,
                "metadata": doc.metadata
            })
        
        return {
            "specialty": specialty,
            "band": band,
            "documents": formatted_docs,
            "total_count": len(formatted_docs)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting specialty documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting specialty documents: {str(e)}")

@router.get("/knowledge-base/statistics")
async def get_knowledge_base_statistics(current_user: dict = Depends(get_current_user)):
    """Obține statistici despre Knowledge Base"""
    try:
        stats = await knowledge_base_service.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting Knowledge Base statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

# ============================================================================
# AI Integration Service Endpoints
# ============================================================================

class AIEvaluationRequestModel(BaseModel):
    question: Dict[str, Any]
    user_answer: str
    band: str
    specialty: str
    user_context: Optional[Dict[str, Any]] = None

@router.post("/ai/evaluate", response_model=Dict[str, Any])
async def evaluate_with_ai(request: AIEvaluationRequestModel, current_user: dict = Depends(get_current_user)):
    """Evaluează un răspuns folosind toate serviciile AI"""
    try:
        # Creează request AI
        ai_request = AIEvaluationRequest(
            question=request.question,
            user_answer=request.user_answer,
            band=request.band,
            specialty=request.specialty,
            user_context=request.user_context
        )
        
        # Evaluează
        response = await ai_integration_service.evaluate_answer(ai_request)
        
        return {
            "evaluation": {
                "question_id": response.evaluation.question_id,
                "band": response.evaluation.band,
                "specialty": response.evaluation.specialty,
                "overall_score": response.evaluation.overall_score,
                "detailed_scores": response.evaluation.detailed_scores,
                "feedback": response.evaluation.feedback,
                "strengths": response.evaluation.strengths,
                "areas_for_improvement": response.evaluation.areas_for_improvement,
                "knowledge_gaps": response.evaluation.knowledge_gaps,
                "book_recommendations": response.evaluation.book_recommendations,
                "next_steps": response.evaluation.next_steps
            },
            "context_used": response.context_used,
            "recommendations": response.recommendations,
            "knowledge_sources": response.knowledge_sources,
            "processing_time": response.processing_time
        }
        
    except Exception as e:
        logger.error(f"❌ Error in AI evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI evaluation error: {str(e)}")

# ============================================================================
# Health Check Endpoints
# ============================================================================

@router.get("/health/rag")
async def rag_health_check(current_user: dict = Depends(get_current_user)):
    """Verifică starea serviciului RAG"""
    try:
        health = await rag_service.health_check()
        return health
        
    except Exception as e:
        logger.error(f"❌ Error in RAG health check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG health check error: {str(e)}")

@router.get("/health/mcp")
async def mcp_health_check(current_user: dict = Depends(get_current_user)):
    """Verifică starea serviciului MCP"""
    try:
        health = await mcp_service.health_check()
        return health
        
    except Exception as e:
        logger.error(f"❌ Error in MCP health check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"MCP health check error: {str(e)}")

@router.get("/health/knowledge-base")
async def knowledge_base_health_check(current_user: dict = Depends(get_current_user)):
    """Verifică starea serviciului Knowledge Base"""
    try:
        health = await knowledge_base_service.health_check()
        return health
        
    except Exception as e:
        logger.error(f"❌ Error in Knowledge Base health check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Knowledge Base health check error: {str(e)}")

@router.get("/health/all")
async def all_services_health_check(current_user: dict = Depends(get_current_user)):
    """Verifică starea tuturor serviciilor AI"""
    try:
        health = await ai_integration_service.health_check()
        return health
        
    except Exception as e:
        logger.error(f"❌ Error in all services health check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"All services health check error: {str(e)}")

# ============================================================================
# Initialization Endpoint
# ============================================================================

@router.post("/initialize")
async def initialize_ai_services(background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """Inițializează toate serviciile AI"""
    try:
        # Inițializează în background
        background_tasks.add_task(ai_integration_service.initialize)
        
        return {
            "message": "AI services initialization started",
            "status": "initializing"
        }
        
    except Exception as e:
        logger.error(f"❌ Error initializing AI services: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI services initialization error: {str(e)}")
