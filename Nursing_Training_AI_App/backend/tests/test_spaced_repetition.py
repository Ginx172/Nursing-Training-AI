"""
Tests for spaced repetition algorithm and interval logic.
"""
import os
import sys
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "ci-test-secret-key-minimum-32-characters-long")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.spaced_repetition_service import SpacedRepetitionService, INTERVALS


class TestIntervals:
    def test_intervals_increasing(self):
        """Intervalele trebuie sa creasca"""
        for i in range(len(INTERVALS) - 1):
            assert INTERVALS[i] < INTERVALS[i + 1], f"Interval {i} not increasing"

    def test_first_interval_is_one_day(self):
        assert INTERVALS[0] == 1

    def test_max_interval_is_60_days(self):
        assert INTERVALS[-1] == 60


class TestQuestionMix:
    def test_service_instantiation(self):
        srs = SpacedRepetitionService()
        assert srs is not None

    def test_format_question_has_required_fields(self):
        srs = SpacedRepetitionService()

        class MockRow:
            id = 1
            title = "Test Question"
            question_text = "What is..."
            question_type = None
            difficulty_level = None
            nhs_band = "band_5"
            specialization = "amu"

        result = srs._format_question(MockRow(), "test_reason")
        assert result["id"] == 1
        assert result["title"] == "Test Question"
        assert result["source_reason"] == "test_reason"
        assert "band" in result
        assert "specialty" in result
