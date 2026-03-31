"""
Tests for question quality scoring logic.
"""
import os
import sys
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "ci-test-secret-key-minimum-32-characters-long")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.question_quality_service import QuestionQualityService, GENERIC_PATTERNS


class MockQuestion:
    def __init__(self, answer="", explanation=None, options=None, tags=None, title="Test"):
        self.correct_answer = answer
        self.explanation = explanation
        self.options = options
        self.tags = tags
        self.title = title


class TestQualityScoring:
    @pytest.fixture
    def service(self):
        return QuestionQualityService()

    def test_generic_answer_low_score(self, service):
        q = MockQuestion(answer="Assess fever using appropriate assessment tools; Monitor vital signs")
        score = service.calculate_quality_score(q)
        assert score < 50, f"Generic answer should score low, got {score}"

    def test_detailed_answer_high_score(self, service):
        q = MockQuestion(
            answer="For sepsis recognition, use the NEWS2 scoring system. " * 20,  # Long, specific
            explanation="Based on NICE NG51 guidelines, sepsis requires immediate assessment.",
            tags=["sepsis", "emergency", "assessment"],
            title="Sepsis Recognition Protocol",
        )
        score = service.calculate_quality_score(q)
        assert score >= 60, f"Detailed answer should score high, got {score}"

    def test_empty_answer_low_score(self, service):
        q = MockQuestion(answer="")
        score = service.calculate_quality_score(q)
        # Empty answer still gets non-generic bonus (30) since empty doesn't match patterns
        assert score <= 40

    def test_long_answer_gets_length_points(self, service):
        short = MockQuestion(answer="Short answer here")
        long = MockQuestion(answer="Detailed clinical answer " * 30)
        assert service.calculate_quality_score(long) > service.calculate_quality_score(short)

    def test_with_options_gets_bonus(self, service):
        without = MockQuestion(answer="Answer text " * 10)
        with_opts = MockQuestion(answer="Answer text " * 10, options=["A", "B", "C", "D"])
        assert service.calculate_quality_score(with_opts) > service.calculate_quality_score(without)

    def test_max_score_is_100(self, service):
        q = MockQuestion(
            answer="Very long specific clinical answer " * 50,
            explanation="Detailed explanation based on NICE guidelines" * 5,
            options=["A", "B", "C", "D"],
            tags=["tag1", "tag2", "tag3"],
            title="Very descriptive question title",
        )
        score = service.calculate_quality_score(q)
        assert score <= 100


class TestGenericPatterns:
    def test_patterns_exist(self):
        assert len(GENERIC_PATTERNS) > 0

    def test_common_generic_detected(self):
        generic_text = "Assess fever using appropriate assessment tools"
        assert any(p.lower() in generic_text.lower() for p in GENERIC_PATTERNS)

    def test_specific_text_not_generic(self):
        specific = "Administer paracetamol 1g PO as per BNF dosing guidelines"
        assert not any(p.lower() in specific.lower() for p in GENERIC_PATTERNS)
