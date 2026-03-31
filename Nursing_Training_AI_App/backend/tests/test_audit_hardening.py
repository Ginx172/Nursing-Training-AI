"""
Tests for audit service hardening: rate limiting, sanitization, field limits.
"""
import os
import sys
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "ci-test-secret-key-minimum-32-characters-long")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.audit_service import AuditService, AuditAction, AuditSeverity


@pytest.fixture
def audit():
    return AuditService()


class TestSanitization:
    def test_sanitize_string_none(self, audit):
        assert audit._sanitize_string(None) is None

    def test_sanitize_string_truncation(self, audit):
        long_str = "A" * 1000
        result = audit._sanitize_string(long_str)
        assert len(result) == audit.MAX_STRING_FIELD

    def test_sanitize_string_control_chars(self, audit):
        dirty = "hello\x00world\x01test"
        result = audit._sanitize_string(dirty)
        assert "\x00" not in result
        assert "\x01" not in result
        assert "hello" in result

    def test_sanitize_details_empty(self, audit):
        assert audit._sanitize_details(None) == {}
        assert audit._sanitize_details({}) == {}

    def test_sanitize_details_redacts_secrets(self, audit):
        details = {
            "password": "secret123",
            "token": "abc-xyz",
            "api_key": "sk-12345",
            "normal_field": "safe value",
        }
        result = audit._sanitize_details(details)
        assert result["password"] == "[REDACTED]"
        assert result["token"] == "[REDACTED]"
        assert result["api_key"] == "[REDACTED]"
        assert result["normal_field"] == "safe value"

    def test_sanitize_details_truncates_large(self, audit):
        details = {"big_field": "X" * 10000}
        result = audit._sanitize_details(details)
        # Field should be truncated
        assert len(result.get("big_field", "")) < 10000

    def test_sanitize_details_size_limit(self, audit):
        # Create details larger than MAX_DETAILS_SIZE
        huge = {"data": "Y" * (audit.MAX_DETAILS_SIZE + 1000)}
        result = audit._sanitize_details(huge)
        assert "_truncated" in result or len(str(result)) <= audit.MAX_DETAILS_SIZE + 200


class TestRateLimiting:
    def test_rate_limit_allows_normal(self, audit):
        assert audit._check_rate_limit("user1") is True
        assert audit._check_rate_limit("user1") is True

    def test_rate_limit_blocks_excess(self, audit):
        user = "flood_user"
        for i in range(audit.RATE_LIMIT_MAX):
            assert audit._check_rate_limit(user) is True
        # Next one should be blocked
        assert audit._check_rate_limit(user) is False

    def test_rate_limit_per_user(self, audit):
        for i in range(audit.RATE_LIMIT_MAX):
            audit._check_rate_limit("user_a")
        # user_a is blocked
        assert audit._check_rate_limit("user_a") is False
        # user_b is not affected
        assert audit._check_rate_limit("user_b") is True

    def test_rate_limit_anonymous(self, audit):
        assert audit._check_rate_limit(None) is True


class TestLogRotation:
    def test_rotation_trims_logs(self, audit):
        # Fill beyond max
        for i in range(audit.MAX_IN_MEMORY_LOGS + 100):
            audit.logs.append({"id": i})
        audit._rotate_in_memory_logs()
        assert len(audit.logs) <= audit.MAX_IN_MEMORY_LOGS
