"""
SDK Exceptions
"""

class NursingAIException(Exception):
    """Base exception for Nursing AI SDK"""
    pass

class AuthenticationError(NursingAIException):
    """Authentication failed"""
    pass

class RateLimitError(NursingAIException):
    """Rate limit exceeded"""
    pass

class ResourceNotFoundError(NursingAIException):
    """Resource not found"""
    pass

class ValidationError(NursingAIException):
    """Validation error"""
    pass

