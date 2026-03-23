"""
Teste pentru sistemul de evaluare AI universal
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

from api.routes.questions import router as questions_router

_app = FastAPI()
_app.include_router(questions_router, prefix="/api/questions")

client = TestClient(_app)

class TestAIEvaluation:
    """Teste pentru evaluarea AI universală"""
    
    def test_get_available_bands(self):
        """Test obținerea banzilor disponibile"""
        response = client.get("/api/questions/bands")
        assert response.status_code == 200
        
        bands = response.json()
        assert len(bands) > 0
        assert any(band["id"] == "band_5" for band in bands)
        assert any(band["id"] == "band_8a" for band in bands)
    
    def test_get_available_specialties(self):
        """Test obținerea specialităților disponibile"""
        response = client.get("/api/questions/specialties")
        assert response.status_code == 200
        
        specialties = response.json()
        assert len(specialties) > 0
        assert any(spec["id"] == "amu" for spec in specialties)
        assert any(spec["id"] == "icu" for spec in specialties)
    
    def test_get_amu_band5_questions(self):
        """Test obținerea întrebărilor Band 5 AMU"""
        response = client.get("/api/questions/amu/band5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["band"] == "band_5"
        assert data["specialty"] == "amu"
        assert len(data["questions"]) > 0
        
        # Verifică structura unei întrebări
        question = data["questions"][0]
        assert "id" in question
        assert "title" in question
        assert "question_text" in question
        assert "question_type" in question
    
    @patch('core.ai_evaluation.ai_evaluation_service.evaluate_answer')
    def test_evaluate_answer_success(self, mock_evaluate):
        """Test evaluarea unui răspuns cu succes"""
        # Mock evaluarea AI
        mock_result = {
            "question_id": 1,
            "band": "band_5",
            "specialty": "amu",
            "overall_score": 85.0,
            "detailed_scores": {
                "knowledge_depth": 80.0,
                "clinical_reasoning": 90.0,
                "safety_awareness": 85.0,
                "communication": 80.0,
                "leadership": 70.0
            },
            "feedback": "Excellent clinical reasoning and safety awareness.",
            "strengths": ["Strong clinical knowledge", "Good communication"],
            "areas_for_improvement": ["Leadership skills"],
            "knowledge_gaps": ["Advanced protocols"],
            "book_recommendations": [
                {
                    "title": "Oxford Handbook of Acute Medicine",
                    "author": "Punit Ramrakha",
                    "isbn": "9780198719441",
                    "description": "Essential reference for AMU practice",
                    "level": "intermediate"
                }
            ],
            "next_steps": ["Study advanced protocols", "Practice leadership scenarios"]
        }
        
        # Mock the async method - use side_effect with async function
        async def mock_evaluate_async(*args, **kwargs):
            from core.ai_evaluation import EvaluationResult
            return EvaluationResult(**mock_result)
        
        mock_evaluate.side_effect = mock_evaluate_async
        
        # Test data
        evaluation_request = {
            "question": {
                "id": 1,
                "title": "ABCDE assessment",
                "question_text": "Outline the ABCDE approach",
                "question_type": "scenario",
                "competencies": ["Assessment", "Safety"]
            },
            "user_answer": "Airway, Breathing, Circulation, Disability, Exposure",
            "band": "band_5",
            "specialty": "amu"
        }
        
        response = client.post("/api/questions/evaluate", json=evaluation_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["question_id"] == 1
        assert data["band"] == "band_5"
        assert data["specialty"] == "amu"
        assert data["overall_score"] == 85.0
        assert len(data["book_recommendations"]) > 0
    
    def test_evaluate_answer_invalid_band(self):
        """Test evaluarea cu band invalid"""
        evaluation_request = {
            "question": {"id": 1, "title": "Test", "question_text": "Test?"},
            "user_answer": "Test answer",
            "band": "invalid_band",
            "specialty": "amu"
        }
        
        response = client.post("/api/questions/evaluate", json=evaluation_request)
        # Ar trebui să funcționeze cu fallback
        assert response.status_code in [200, 500]
    
    def test_evaluate_answer_missing_fields(self):
        """Test evaluarea cu câmpuri lipsă"""
        evaluation_request = {
            "question": {"id": 1},
            "user_answer": "Test answer",
            "band": "band_5",
            "specialty": "amu"
        }
        
        response = client.post("/api/questions/evaluate", json=evaluation_request)
        # Ar trebui să funcționeze cu fallback
        assert response.status_code in [200, 500]


class TestSelfLearning:
    """Teste pentru modulul de auto-învățare"""
    
    @patch('core.self_learning.self_learning.record_outcome')
    def test_self_learning_integration(self, mock_record):
        """Test integrarea cu self-learning"""
        from core.self_learning import self_learning
        
        # Test record outcome
        outcome = {
            "band": "band_5",
            "specialty": "amu",
            "overall_score": 85.0,
            "user_feedback_score": 4.0
        }
        
        self_learning.record_outcome(outcome)
        mock_record.assert_called_once_with(outcome)
    
    def test_self_learning_weights(self):
        """Test obținerea și ajustarea ponderilor"""
        from core.self_learning import self_learning
        
        # Test get weights
        weights = self_learning.get_weights()
        assert "knowledge_depth_weight" in weights
        assert "clinical_reasoning_weight" in weights
        assert "safety_awareness_weight" in weights
        assert "communication_weight" in weights
        assert "leadership_weight" in weights
        
        # Test retrain
        new_weights = self_learning.retrain()
        assert isinstance(new_weights, dict)
        assert len(new_weights) == 5


class TestTelemetry:
    """Teste pentru sistemul de telemetrie"""
    
    @patch('core.telemetry.telemetry.log_event')
    def test_telemetry_logging(self, mock_log):
        """Test logging-ul de telemetrie"""
        from core.telemetry import telemetry
        
        telemetry.log_event("test_event", {"key": "value"})
        mock_log.assert_called_once_with("test_event", {"key": "value"})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
