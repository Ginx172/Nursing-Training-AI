"""
🤖 AI Integration Service
Serviciu principal care integrează RAG, MCP și Knowledge Base pentru evaluarea AI
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from .rag_service import rag_service, RAGQuery, SearchResult
from .mcp_service import mcp_service, MCPRequest, MCPResponse, ContextType
from .knowledge_base_service import knowledge_base_service, DocumentInfo, SearchResult as KBSearchResult
from core.ai_evaluation import AIEvaluationService, EvaluationResult, BandLevel, Specialty

logger = logging.getLogger(__name__)

@dataclass
class AIEvaluationRequest:
    """Request pentru evaluarea AI"""
    question: Dict[str, Any]
    user_answer: str
    band: str
    specialty: str
    user_context: Optional[Dict[str, Any]] = None

@dataclass
class AIEvaluationResponse:
    """Răspunsul complet de la evaluarea AI"""
    evaluation: EvaluationResult
    context_used: Dict[str, Any]
    recommendations: List[Dict[str, str]]
    knowledge_sources: List[str]
    processing_time: float

class AIIntegrationService:
    """Serviciul principal de integrare AI"""
    
    def __init__(self):
        self.rag_service = rag_service
        self.mcp_service = mcp_service
        self.knowledge_base_service = knowledge_base_service
        self.ai_evaluation_service = AIEvaluationService()
        self.is_initialized = False
    
    async def initialize(self):
        """Inițializează serviciul de integrare AI"""
        try:
            logger.info("🚀 Initializing AI Integration Service...")
            
            # Inițializează toate serviciile
            rag_initialized = await self.rag_service.initialize()
            mcp_initialized = await self.mcp_service.initialize()
            kb_initialized = await self.knowledge_base_service.initialize()
            
            if not all([rag_initialized, mcp_initialized, kb_initialized]):
                logger.warning("⚠️ Some services failed to initialize")
            
            self.is_initialized = True
            logger.info("✅ AI Integration Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing AI Integration Service: {str(e)}")
            return False
    
    async def evaluate_answer(self, request: AIEvaluationRequest) -> AIEvaluationResponse:
        """Evaluează un răspuns folosind toate serviciile AI"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if not self.is_initialized:
                logger.error("❌ AI Integration Service not initialized")
                return self._create_error_response("Service not initialized", start_time)
            
            # 1. Obține context din Knowledge Base
            kb_context = await self._get_knowledge_base_context(request)
            
            # 2. Obține context din RAG
            rag_context = await self._get_rag_context(request)
            
            # 3. Obține context din MCP
            mcp_context = await self._get_mcp_context(request)
            
            # 4. Combină toate contexturile
            combined_context = {
                "knowledge_base": kb_context,
                "rag": rag_context,
                "mcp": mcp_context,
                "question": request.question,
                "user_answer": request.user_answer,
                "band": request.band,
                "specialty": request.specialty
            }
            
            # 5. Evaluează răspunsul folosind AI
            evaluation = await self.ai_evaluation_service.evaluate_answer(
                question=request.question,
                user_answer=request.user_answer,
                band=request.band,
                specialty=request.specialty
            )
            
            # 6. Obține recomandări de studiu
            recommendations = await self._get_study_recommendations(request, evaluation)
            
            # 7. Identifică sursele de cunoștințe folosite
            knowledge_sources = self._extract_knowledge_sources(kb_context, rag_context, mcp_context)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return AIEvaluationResponse(
                evaluation=evaluation,
                context_used=combined_context,
                recommendations=recommendations,
                knowledge_sources=knowledge_sources,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Error in AI evaluation: {str(e)}")
            return self._create_error_response(f"Evaluation error: {str(e)}", start_time)
    
    async def _get_knowledge_base_context(self, request: AIEvaluationRequest) -> Dict[str, Any]:
        """Obține context din Knowledge Base"""
        try:
            # Caută documente relevante
            kb_results = await self.knowledge_base_service.search_documents(
                query=request.question.get("question_text", ""),
                specialty=request.specialty,
                band=request.band
            )
            
            # Obține statistici despre specialitate
            specialty_docs = await self.knowledge_base_service.get_specialty_documents(
                specialty=request.specialty,
                band=request.band
            )
            
            return {
                "relevant_documents": [
                    {
                        "title": result.document.title,
                        "relevance_score": result.relevance_score,
                        "file_path": result.document.file_path,
                        "band": result.document.band
                    }
                    for result in kb_results[:5]  # Top 5 documente
                ],
                "total_documents_available": len(specialty_docs),
                "specialty": request.specialty,
                "band": request.band
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting Knowledge Base context: {str(e)}")
            return {"error": str(e)}
    
    async def _get_rag_context(self, request: AIEvaluationRequest) -> Dict[str, Any]:
        """Obține context din RAG"""
        try:
            # Creează query RAG
            rag_query = RAGQuery(
                query_text=request.question.get("question_text", ""),
                specialty=request.specialty,
                band=request.band,
                max_results=5,
                min_score=0.6
            )
            
            # Caută în RAG
            rag_results = await self.rag_service.search(rag_query)
            
            return {
                "relevant_chunks": [
                    {
                        "content": result.content[:200] + "..." if len(result.content) > 200 else result.content,
                        "source": result.source,
                        "score": result.score,
                        "metadata": result.metadata
                    }
                    for result in rag_results
                ],
                "total_chunks_found": len(rag_results),
                "specialty": request.specialty
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting RAG context: {str(e)}")
            return {"error": str(e)}
    
    async def _get_mcp_context(self, request: AIEvaluationRequest) -> Dict[str, Any]:
        """Obține context din MCP"""
        try:
            # Creează request MCP
            mcp_request = MCPRequest(
                query=request.question.get("question_text", ""),
                context_type=ContextType.QUESTION_EVALUATION,
                specialty=request.specialty,
                band=request.band,
                user_data=request.user_context,
                additional_context=f"User answer: {request.user_answer}"
            )
            
            # Procesează cu MCP
            mcp_response = await self.mcp_service.process_request(mcp_request)
            
            return {
                "mcp_response": mcp_response.response,
                "model_used": mcp_response.model_used,
                "confidence": mcp_response.confidence,
                "context_used": mcp_response.context_used,
                "metadata": mcp_response.metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting MCP context: {str(e)}")
            return {"error": str(e)}
    
    async def _get_study_recommendations(self, request: AIEvaluationRequest, evaluation: EvaluationResult) -> List[Dict[str, str]]:
        """Obține recomandări de studiu"""
        try:
            # Obține recomandări din RAG
            rag_recommendations = await self.rag_service.get_recommendations(
                question=request.question.get("question_text", ""),
                specialty=request.specialty,
                band=request.band
            )
            
            # Adaugă recomandări din Knowledge Base
            kb_docs = await self.knowledge_base_service.get_specialty_documents(
                specialty=request.specialty,
                band=request.band
            )
            
            kb_recommendations = [
                {
                    "title": doc.title,
                    "summary": f"Document for {doc.specialty} - {doc.band}",
                    "source": doc.file_path,
                    "type": "document"
                }
                for doc in kb_docs[:3]  # Top 3 documente
            ]
            
            # Combină recomandările
            all_recommendations = rag_recommendations + kb_recommendations
            
            # Adaugă recomandări bazate pe evaluare
            if evaluation.knowledge_gaps:
                gap_recommendations = [
                    {
                        "title": f"Study: {gap}",
                        "summary": f"Focus on improving knowledge in: {gap}",
                        "source": "AI Evaluation",
                        "type": "knowledge_gap"
                    }
                    for gap in evaluation.knowledge_gaps[:3]
                ]
                all_recommendations.extend(gap_recommendations)
            
            return all_recommendations[:10]  # Limitează la 10 recomandări
            
        except Exception as e:
            logger.error(f"❌ Error getting study recommendations: {str(e)}")
            return []
    
    def _extract_knowledge_sources(self, kb_context: Dict[str, Any], rag_context: Dict[str, Any], mcp_context: Dict[str, Any]) -> List[str]:
        """Extrage sursele de cunoștințe folosite"""
        sources = []
        
        # Surse din Knowledge Base
        if "relevant_documents" in kb_context:
            for doc in kb_context["relevant_documents"]:
                sources.append(f"Knowledge Base: {doc['title']}")
        
        # Surse din RAG
        if "relevant_chunks" in rag_context:
            for chunk in rag_context["relevant_chunks"]:
                sources.append(f"RAG: {chunk['source']}")
        
        # Surse din MCP
        if "model_used" in mcp_context:
            sources.append(f"MCP: {mcp_context['model_used']}")
        
        return list(set(sources))  # Elimină duplicatele
    
    def _create_error_response(self, error_message: str, start_time: float) -> AIEvaluationResponse:
        """Creează un răspuns de eroare"""
        processing_time = asyncio.get_event_loop().time() - start_time
        
        return AIEvaluationResponse(
            evaluation=EvaluationResult(
                question_id=0,
                band="unknown",
                specialty="unknown",
                overall_score=0.0,
                detailed_scores={},
                feedback=f"Error: {error_message}",
                strengths=[],
                areas_for_improvement=[],
                knowledge_gaps=[],
                book_recommendations=[],
                next_steps=[]
            ),
            context_used={"error": error_message},
            recommendations=[],
            knowledge_sources=[],
            processing_time=processing_time
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifică starea serviciului de integrare AI"""
        try:
            rag_health = await self.rag_service.health_check()
            mcp_health = await self.mcp_service.health_check()
            kb_health = await self.knowledge_base_service.health_check()
            
            return {
                "initialized": self.is_initialized,
                "rag_service": rag_health,
                "mcp_service": mcp_health,
                "knowledge_base_service": kb_health,
                "all_services_healthy": all([
                    rag_health.get("initialized", False),
                    mcp_health.get("initialized", False),
                    kb_health.get("initialized", False)
                ])
            }
            
        except Exception as e:
            logger.error(f"❌ Error in health check: {str(e)}")
            return {
                "initialized": self.is_initialized,
                "error": str(e)
            }

# Instanță globală a serviciului
ai_integration_service = AIIntegrationService()
