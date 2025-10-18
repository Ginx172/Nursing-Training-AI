"""
Nursing Training AI - Python SDK
Official Python client library for Enterprise API integration
"""

__version__ = "1.0.0"
__author__ = "Nursing Training AI"
__email__ = "developers@nursingtrainingai.com"

from .client import NursingAIClient
from .models import User, Question, QuestionBank, Analytics, Subscription
from .exceptions import (
    NursingAIException,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError
)

__all__ = [
    "NursingAIClient",
    "User",
    "Question",
    "QuestionBank",
    "Analytics",
    "Subscription",
    "NursingAIException",
    "AuthenticationError",
    "RateLimitError",
    "ResourceNotFoundError",
    "ValidationError"
]

