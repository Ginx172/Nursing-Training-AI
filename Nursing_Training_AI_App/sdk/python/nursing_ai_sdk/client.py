"""
Nursing AI SDK Client
Main client class for interacting with the API
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from .exceptions import (
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
    NursingAIException
)
from .models import User, Question, QuestionBank, Analytics

class NursingAIClient:
    """
    Official Python client for Nursing Training AI API
    
    Example usage:
        >>> client = NursingAIClient(api_key="your_api_key")
        >>> user = client.users.get("user_123")
        >>> questions = client.questions.search(specialty="amu", band="band_5")
        >>> analytics = client.analytics.get_user_analytics("user_123")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.nursingtrainingai.com",
        timeout: int = 30
    ):
        """
        Initialize Nursing AI client
        
        Args:
            api_key: API key for authentication (Enterprise only)
            base_url: Base URL for API (default: production)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                "X-API-Key": api_key,
                "User-Agent": f"NursingAI-Python-SDK/1.0.0"
            })
        
        # Initialize resource clients
        self.users = UserResource(self)
        self.questions = QuestionResource(self)
        self.analytics = AnalyticsResource(self)
        self.subscriptions = SubscriptionResource(self)
        self.organizations = OrganizationResource(self)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            # Handle errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or unauthorized")
            elif response.status_code == 403:
                raise AuthenticationError("Insufficient permissions")
            elif response.status_code == 404:
                raise ResourceNotFoundError("Resource not found")
            elif response.status_code == 422:
                raise ValidationError(f"Validation error: {response.json()}")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 500:
                raise NursingAIException(f"Server error: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            raise NursingAIException(f"Request failed: {str(e)}")

# ========================================
# RESOURCE CLASSES
# ========================================

class UserResource:
    """User resource operations"""
    
    def __init__(self, client: NursingAIClient):
        self.client = client
    
    def get(self, user_id: str) -> User:
        """Get user by ID"""
        data = self.client._request("GET", f"/api/users/{user_id}")
        return User(**data["user"])
    
    def list(self, limit: int = 50, offset: int = 0) -> List[User]:
        """List users (Admin only)"""
        data = self.client._request(
            "GET",
            "/api/admin/users/search",
            params={"limit": limit, "offset": offset}
        )
        return [User(**u) for u in data["users"]]
    
    def update(self, user_id: str, updates: Dict) -> User:
        """Update user"""
        data = self.client._request(
            "PUT",
            f"/api/admin/users/{user_id}",
            json=updates
        )
        return User(**data["user"])

class QuestionResource:
    """Question resource operations"""
    
    def __init__(self, client: NursingAIClient):
        self.client = client
    
    def get_bank(
        self,
        sector: str,
        specialty: str,
        band: str,
        bank_number: int
    ) -> QuestionBank:
        """Get question bank"""
        data = self.client._request(
            "GET",
            f"/api/questions/{sector}/{specialty}/{band}/{bank_number}"
        )
        return QuestionBank(**data)
    
    def search(self, **filters) -> List[Question]:
        """Search questions"""
        data = self.client._request(
            "GET",
            "/api/admin/questions/search",
            params=filters
        )
        return [Question(**q) for q in data["questions"]]

class AnalyticsResource:
    """Analytics resource operations"""
    
    def __init__(self, client: NursingAIClient):
        self.client = client
    
    def get_user_analytics(
        self,
        user_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Analytics:
        """Get user analytics"""
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        
        data = self.client._request(
            "GET",
            f"/api/analytics/user/{user_id}",
            params=params
        )
        return Analytics(**data["analytics"])
    
    def export_report(
        self,
        user_id: str,
        format: str = "json"
    ) -> Dict:
        """Export analytics report"""
        data = self.client._request(
            "GET",
            f"/api/analytics/user/{user_id}/export",
            params={"format": format}
        )
        return data

class SubscriptionResource:
    """Subscription resource operations"""
    
    def __init__(self, client: NursingAIClient):
        self.client = client
    
    def create(
        self,
        user_id: str,
        tier: str,
        billing_cycle: str = "monthly"
    ) -> Dict:
        """Create subscription"""
        data = self.client._request(
            "POST",
            "/api/payments/subscriptions/create",
            json={
                "user_id": user_id,
                "tier": tier,
                "billing_cycle": billing_cycle
            }
        )
        return data
    
    def cancel(self, subscription_id: str, immediately: bool = False) -> Dict:
        """Cancel subscription"""
        data = self.client._request(
            "POST",
            "/api/payments/subscriptions/cancel",
            json={
                "subscription_id": subscription_id,
                "immediately": immediately
            }
        )
        return data

class OrganizationResource:
    """Organization resource operations"""
    
    def __init__(self, client: NursingAIClient):
        self.client = client
    
    def get_team_analytics(
        self,
        organization_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict:
        """Get team analytics (Enterprise only)"""
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        
        data = self.client._request(
            "GET",
            f"/api/analytics/team/{organization_id}",
            params=params
        )
        return data["analytics"]

