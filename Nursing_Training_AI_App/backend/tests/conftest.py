"""
Pytest configuration and fixtures for backend tests.
Sets required environment variables before any module imports occur,
so tests can run without a local .env file.
"""

import os

# Set required environment variables early — before main.py / core.config is imported.
# In CI these are set at the job level; this ensures they are also present for local runs.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "ci-test-secret-key-minimum-32-characters-long")
