"""
AI Evaluation Service pentru toate banzile și specialitățile
Integrează MCP și RAG pentru evaluare inteligentă și recomandări de cărți
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import httpx
from pathlib import Path
from .mcp_rag_config import mcp_rag_config

logger = logging.getLogger(__name__)

class BandLevel(Enum):
    BAND_2 = "band_2"
    BAND_3 = "band_3" 
    BAND_4 = "band_4"
    BAND_5 = "band_5"
    BAND_6 = "band_6"
    BAND_7 = "band_7"
    BAND_8A = "band_8a"
    BAND_8B = "band_8b"
    BAND_8C = "band_8c"
    BAND_8D = "band_8d"
    BAND_9 = "band_9"

class Specialty(Enum):
    AMU = "amu"
    ICU = "icu"
    EMERGENCY = "emergency"
    MATERNITY = "maternity"
    MENTAL_HEALTH = "mental_health"
    PEDIATRICS = "pediatrics"
    ONCOLOGY = "oncology"
    CARDIOLOGY = "cardiology"
    NEUROLOGY = "neurology"

@dataclass
class EvaluationCriteria:
    """Criterii de evaluare pentru fiecare band și specialitate"""
    band: BandLevel
    specialty: Specialty
    knowledge_depth: float  # 0.0-1.0
    clinical_reasoning: float  # 0.0-1.0
    safety_awareness: float  # 0.0-1.0
    communication: float  # 0.0-1.0
    leadership: float  # 0.0-1.0 (pentru banzile superioare)

@dataclass
class EvaluationResult:
    """Rezultatul evaluării AI"""
    question_id: int
    band: str
    specialty: str
    overall_score: float  # 0-100
    detailed_scores: Dict[str, float]
    feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]
    knowledge_gaps: List[str]
    book_recommendations: List[Dict[str, str]]
    next_steps: List[str]

class AIEvaluationService:
    """Serviciul principal de evaluare AI cu MCP și RAG"""
    
    def __init__(self):
        self.knowledge_base_path = Path(mcp_rag_config.knowledge_base_path)
        self.mcp_endpoint = mcp_rag_config.mcp_endpoint
        self.rag_endpoint = mcp_rag_config.rag_endpoint
        self.gemini_api_key = mcp_rag_config.gemini_api_key
        self.gemini_model = mcp_rag_config.gemini_model
        # kept for backward compat
        self.openai_api_key = mcp_rag_config.openai_api_key
        
        # Criterii de evaluare pentru fiecare band
        self.evaluation_criteria = self._load_evaluation_criteria()
        
        # Cărți recomandate pentru fiecare specialitate
        self.book_recommendations = self._load_book_recommendations()
    
    def _load_evaluation_criteria(self) -> Dict[str, EvaluationCriteria]:
        """Încarcă criteriile de evaluare pentru fiecare band"""
        criteria = {}
        
        # Band 5 - Staff Nurse
        criteria["band_5"] = EvaluationCriteria(
            band=BandLevel.BAND_5,
            specialty=Specialty.AMU,
            knowledge_depth=0.7,
            clinical_reasoning=0.6,
            safety_awareness=0.8,
            communication=0.7,
            leadership=0.3
        )
        
        # Band 6 - Senior Staff Nurse
        criteria["band_6"] = EvaluationCriteria(
            band=BandLevel.BAND_6,
            specialty=Specialty.AMU,
            knowledge_depth=0.8,
            clinical_reasoning=0.8,
            safety_awareness=0.9,
            communication=0.8,
            leadership=0.6
        )
        
        # Band 7 - Clinical Nurse Specialist
        criteria["band_7"] = EvaluationCriteria(
            band=BandLevel.BAND_7,
            specialty=Specialty.AMU,
            knowledge_depth=0.9,
            clinical_reasoning=0.9,
            safety_awareness=0.95,
            communication=0.9,
            leadership=0.8
        )
        
        # Band 8A - Advanced Nurse Practitioner
        criteria["band_8a"] = EvaluationCriteria(
            band=BandLevel.BAND_8A,
            specialty=Specialty.AMU,
            knowledge_depth=0.95,
            clinical_reasoning=0.95,
            safety_awareness=0.98,
            communication=0.95,
            leadership=0.9
        )
        
        return criteria
    
    def _load_book_recommendations(self) -> Dict[str, List[Dict[str, str]]]:
        """Încarcă recomandările de cărți pentru fiecare specialitate"""
        return {
            "amu": [
                {
                    "title": "Oxford Handbook of Acute Medicine",
                    "author": "Punit Ramrakha, Kevin Moore, Amir Sam",
                    "isbn": "9780198719441",
                    "description": "Essential reference for AMU practice with evidence-based protocols",
                    "level": "intermediate"
                },
                {
                    "title": "Acute Medical Emergencies: The Practical Approach",
                    "author": "Advanced Life Support Group",
                    "isbn": "9781119120060",
                    "description": "Comprehensive guide to acute medical emergencies and management",
                    "level": "advanced"
                },
                {
                    "title": "Nursing Practice: Knowledge and Care",
                    "author": "Ian Peate, Karen Wild",
                    "isbn": "9781119657004",
                    "description": "Core nursing knowledge for acute care settings",
                    "level": "foundation"
                }
            ],
            "icu": [
                {
                    "title": "Oh's Intensive Care Manual",
                    "author": "Andrew Bersten, Neil Soni",
                    "isbn": "9780702047626",
                    "description": "Comprehensive ICU reference for critical care nursing",
                    "level": "advanced"
                },
                {
                    "title": "Critical Care Nursing: Diagnosis and Management",
                    "author": "Linda D. Urden, Kathleen M. Stacy, Mary E. Lough",
                    "isbn": "9780323460136",
                    "description": "Evidence-based critical care nursing practice",
                    "level": "intermediate"
                }
            ],
            "emergency": [
                {
                    "title": "Emergency Care and Transportation of the Sick and Injured",
                    "author": "American Academy of Orthopaedic Surgeons",
                    "isbn": "9781284104882",
                    "description": "Comprehensive emergency care protocols and procedures",
                    "level": "intermediate"
                }
            ]
        }
    
    async def _query_knowledge_base(self, query: str, specialty: str) -> str:
        """Interoghează knowledge base-ul folosind RAG"""
        try:
            specialty_config = mcp_rag_config.get_specialty_config(specialty)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.rag_endpoint}/query",
                    json={
                        "query": query,
                        "specialty": specialty,
                        "faiss_index": specialty_config.get("faiss_index", "General"),
                        "priority_topics": specialty_config.get("priority_topics", []),
                        "max_results": 5
                    },
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("answer", "")
                else:
                    return f"Knowledge base query failed: {response.status_code}"
        except Exception as e:
            return f"Error querying knowledge base: {str(e)}"
    
    async def _query_mcp(self, query: str, context: Dict[str, Any]) -> str:
        """Interoghează MCP pentru informații suplimentare"""
        try:
            specialty = context.get("specialty", "general")
            mcp_template = mcp_rag_config.get_mcp_query_template(specialty)
            formatted_query = mcp_template.format(query=query)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mcp_endpoint}/query",
                    json={
                        "query": formatted_query,
                        "context": context,
                        "specialty": specialty
                    },
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
                else:
                    return f"MCP query failed: {response.status_code}"
        except Exception as e:
            return f"Error querying MCP: {str(e)}"
    
    async def _get_ai_evaluation(self, question: Dict[str, Any], user_answer: str, 
                                band: str, specialty: str) -> Dict[str, Any]:
        """Obține evaluarea AI folosind Gemini API"""
        if not self.gemini_api_key:
            return self._fallback_evaluation(question, user_answer, band, specialty)
        
        # Construiește prompt-ul pentru evaluare
        criteria = self.evaluation_criteria.get(band)
        if not criteria:
            criteria = self.evaluation_criteria["band_5"]  # fallback
        
        # Interoghează knowledge base-ul pentru context
        kb_context = await self._query_knowledge_base(
            f"Best practices for {question.get('title', '')} in {specialty} for {band}",
            specialty
        )
        
        # Interoghează MCP pentru informații suplimentare
        mcp_context = await self._query_mcp(
            f"Clinical guidelines for {question.get('title', '')}",
            {"band": band, "specialty": specialty, "question_type": question.get("question_type")}
        )
        
        prompt = f"""
        Evaluează următorul răspuns de la un asistent medical {band} în specialitatea {specialty}:

        ÎNTREBAREA: {question.get('question_text', '')}
        TIPUL: {question.get('question_type', '')}
        COMPETENȚE: {', '.join(question.get('competencies', []))}
        PUNCTE AȘTEPTATE: {', '.join(question.get('expected_points', []))}

        RĂSPUNSUL UTILIZATORULUI: {user_answer}

        CONTEXT DIN KNOWLEDGE BASE: {kb_context}
        CONTEXT DIN MCP: {mcp_context}

        CRITERII DE EVALUARE PENTRU {band.upper()}:
        - Profunzimea cunoștințelor: {criteria.knowledge_depth}
        - Raționamentul clinic: {criteria.clinical_reasoning}
        - Conștientizarea siguranței: {criteria.safety_awareness}
        - Comunicarea: {criteria.communication}
        - Leadership-ul: {criteria.leadership}

        Returnează evaluarea în format JSON (doar JSON, fără markdown):
        {{
            "overall_score": 0-100,
            "detailed_scores": {{
                "knowledge_depth": 0-100,
                "clinical_reasoning": 0-100,
                "safety_awareness": 0-100,
                "communication": 0-100,
                "leadership": 0-100
            }},
            "feedback": "Feedback detaliat...",
            "strengths": ["puncte forte"],
            "areas_for_improvement": ["zone de îmbunătățire"],
            "knowledge_gaps": ["lacune în cunoștințe"],
            "next_steps": ["pași următori"]
        }}
        """
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel(self.gemini_model)
            response = model.generate_content(prompt)
            content = response.text.strip()
            # Strip markdown code fences if present
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.rsplit("```", 1)[0].strip()
            return json.loads(content)
        except Exception as exc:
            logger.warning("Gemini API evaluation failed, using fallback: %s", exc)
            return self._fallback_evaluation(question, user_answer, band, specialty)
    
    def _fallback_evaluation(self, question: Dict[str, Any], user_answer: str, 
                           band: str, specialty: str) -> Dict[str, Any]:
        """Evaluare de fallback când AI-ul nu este disponibil"""
        return {
            "overall_score": 75.0,
            "detailed_scores": {
                "knowledge_depth": 70.0,
                "clinical_reasoning": 75.0,
                "safety_awareness": 80.0,
                "communication": 70.0,
                "leadership": 60.0
            },
            "feedback": "Evaluare automată de bază. Pentru evaluare detaliată, contactați administratorul.",
            "strengths": ["Răspuns complet", "Structurat logic"],
            "areas_for_improvement": ["Profunzimea cunoștințelor", "Aplicarea practică"],
            "knowledge_gaps": ["Protocoluri specifice", "Ghiduri clinice"],
            "next_steps": ["Studiu suplimentar", "Practică clinică"]
        }
    
    def _get_book_recommendations(self, specialty: str, knowledge_gaps: List[str]) -> List[Dict[str, str]]:
        """Generează recomandări de cărți bazate pe specialitate și lacunele identificate"""
        books = self.book_recommendations.get(specialty, [])
        
        # Filtrează cărțile bazate pe lacunele identificate
        recommended_books = []
        for book in books:
            # Logica simplă de matching - poate fi îmbunătățită
            if any(gap.lower() in book["description"].lower() for gap in knowledge_gaps):
                recommended_books.append(book)
        
        # Dacă nu găsim cărți specifice, returnează primele 2-3
        if not recommended_books:
            recommended_books = books[:3]
        
        return recommended_books
    
    async def evaluate_answer(self, question: Dict[str, Any], user_answer: str, 
                            band: str, specialty: str) -> EvaluationResult:
        """Evaluează un răspuns folosind AI, MCP și RAG"""
        
        # Obține evaluarea AI
        ai_evaluation = await self._get_ai_evaluation(question, user_answer, band, specialty)
        
        # Generează recomandări de cărți
        book_recommendations = self._get_book_recommendations(
            specialty, 
            ai_evaluation.get("knowledge_gaps", [])
        )

        # Feedback loop — trimite rezultatul înapoi la self_learning
        try:
            from .self_learning import self_learning
            self_learning.record_outcome({
                "band": band,
                "specialty": specialty,
                "overall_score": ai_evaluation.get("overall_score", 0.0),
                "detailed_scores": ai_evaluation.get("detailed_scores", {}),
                "question_id": question.get("id", 0),
            })
        except Exception as exc:
            logger.warning("Failed to record outcome in self_learning feedback loop: %s", exc)
        
        return EvaluationResult(
            question_id=question.get("id", 0),
            band=band,
            specialty=specialty,
            overall_score=ai_evaluation.get("overall_score", 0.0),
            detailed_scores=ai_evaluation.get("detailed_scores", {}),
            feedback=ai_evaluation.get("feedback", ""),
            strengths=ai_evaluation.get("strengths", []),
            areas_for_improvement=ai_evaluation.get("areas_for_improvement", []),
            knowledge_gaps=ai_evaluation.get("knowledge_gaps", []),
            book_recommendations=book_recommendations,
            next_steps=ai_evaluation.get("next_steps", [])
        )

# Instanță globală a serviciului
ai_evaluation_service = AIEvaluationService()
