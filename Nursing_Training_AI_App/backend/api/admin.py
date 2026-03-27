"""
Admin API Endpoints
Admin panel for managing users, content, and platform
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

from models.user import User
from api.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Request/Response Models

class AdminUser(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str  # admin, super_admin

class UserSearchRequest(BaseModel):
    search_term: Optional[str] = None
    sector: Optional[str] = None
    band: Optional[str] = None
    subscription_tier: Optional[str] = None
    status: Optional[str] = None  # active, inactive, trial, cancelled
    limit: int = 50
    offset: int = 0

class UpdateUserRequest(BaseModel):
    user_id: str
    updates: Dict[str, Any]

class CreateQuestionRequest(BaseModel):
    sector: str
    specialty: str
    band: str
    question_type: str
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    competencies: List[str]
    difficulty: str

# USER MANAGEMENT ENDPOINTS

@router.get("/users/search")
async def search_users(
    search_term: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    band: Optional[str] = Query(None),
    subscription_tier: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    admin: User = Depends(get_current_admin),
):
    """Search and filter users (Admin only)"""
    try:
        # TODO: Implement actual database query
        
        users = [
            {
                "id": "user_001",
                "name": "Sarah Johnson",
                "email": "sarah.j@nhs.net",
                "nmc_number": "12A3456E",
                "current_band": "band_6",
                "sector": "nhs",
                "specialty": "emergency",
                "subscription_tier": "professional",
                "status": "active",
                "joined_date": "2025-01-15",
                "last_active": "2025-10-18",
                "questions_completed": 456,
                "accuracy": 85.2,
                "total_spent_gbp": 199.00
            },
            # ... more users
        ]
        
        return {
            "success": True,
            "users": users,
            "total": len(users),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Operation failed. Check server logs for details.")

@router.get("/users/{user_id}")
async def get_user_details(user_id: str, admin: User = Depends(get_current_admin)):
    """Get detailed user information (Admin only)"""
    try:
        # TODO: Fetch from database
        
        user_details = {
            "id": user_id,
            "profile": {
                "name": "Sarah Johnson",
                "email": "sarah.j@nhs.net",
                "nmc_number": "12A3456E",
                "phone": "+44 7700 900123",
                "current_band": "band_6",
                "sector": "nhs",
                "specialty": "emergency"
            },
            "subscription": {
                "tier": "professional",
                "status": "active",
                "billing_cycle": "annual",
                "next_billing_date": "2026-01-15",
                "amount_gbp": 199.00,
                "stripe_customer_id": "cus_example",
                "stripe_subscription_id": "sub_example"
            },
            "activity": {
                "joined_date": "2025-01-15",
                "last_active": "2025-10-18",
                "total_logins": 234,
                "questions_completed": 456,
                "accuracy": 85.2,
                "streak_current": 7,
                "streak_longest": 21
            },
            "permissions": {
                "specialties_access": ["all"],
                "sectors_access": ["all"],
                "bands_access": ["all"],
                "features": ["audio", "offline", "certificates"]
            }
        }
        
        return {
            "success": True,
            "user": user_details
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found or server error.")

@router.put("/users/{user_id}")
async def update_user(user_id: str, updates: Dict[str, Any] = Body(...), admin: User = Depends(get_current_admin)):
    """Update user information (Admin only)"""
    try:
        # TODO: Update database
        
        return {
            "success": True,
            "message": "User updated successfully",
            "user_id": user_id,
            "updated_fields": list(updates.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Operation failed. Check server logs for details.")

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin: User = Depends(get_current_admin)):
    """Delete user account (Admin only)"""
    try:
        # TODO: Delete from database
        # TODO: Cancel Stripe subscription
        
        return {
            "success": True,
            "message": "User deleted successfully",
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Operation failed. Check server logs for details.")

# CONTENT MANAGEMENT ENDPOINTS

@router.get("/questions/search")
async def search_questions(
    sector: Optional[str] = Query(None),
    specialty: Optional[str] = Query(None),
    band: Optional[str] = Query(None),
    question_type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    admin: User = Depends(get_current_admin),
):
    """Search questions (Admin only)"""
    try:
        # TODO: Implement database query
        
        questions = []  # Fetch from database
        
        return {
            "success": True,
            "questions": questions,
            "total": len(questions),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Operation failed. Check server logs for details.")

@router.post("/questions/create")
async def create_question(question: CreateQuestionRequest, admin: User = Depends(get_current_admin)):
    """Create new question (Admin only)"""
    try:
        # TODO: Save to database
        
        return {
            "success": True,
            "message": "Question created successfully",
            "question_id": "q_new_001"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Operation failed. Check server logs for details.")

@router.put("/questions/{question_id}")
async def update_question(question_id: str, updates: Dict[str, Any] = Body(...), admin: User = Depends(get_current_admin)):
    """Update question (Admin only)"""
    try:
        # TODO: Update database
        
        return {
            "success": True,
            "message": "Question updated successfully",
            "question_id": question_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Operation failed. Check server logs for details.")

@router.delete("/questions/{question_id}")
async def delete_question(question_id: str, admin: User = Depends(get_current_admin)):
    """Delete question (Admin only)"""
    try:
        # TODO: Delete from database
        
        return {
            "success": True,
            "message": "Question deleted successfully",
            "question_id": question_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Operation failed. Check server logs for details.")

# SUBSCRIPTION MANAGEMENT ENDPOINTS

@router.get("/subscriptions")
async def get_all_subscriptions(
    status: Optional[str] = Query(None),
    tier: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    admin: User = Depends(get_current_admin),
):
    """Get all subscriptions (Admin only)"""
    try:
        # TODO: Fetch from database and Stripe
        
        subscriptions = []
        
        return {
            "success": True,
            "subscriptions": subscriptions,
            "total": len(subscriptions)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Operation failed. Check server logs for details.")

@router.post("/subscriptions/{subscription_id}/cancel")
async def admin_cancel_subscription(subscription_id: str, reason: str = Body(...), admin: User = Depends(get_current_admin)):
    """Cancel subscription as admin"""
    try:
        # TODO: Cancel in Stripe
        # TODO: Update database
        # TODO: Send notification to user
        
        return {
            "success": True,
            "message": "Subscription cancelled",
            "subscription_id": subscription_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Operation failed. Check server logs for details.")

# SYSTEM CONFIGURATION ENDPOINTS

@router.get("/config")
async def get_system_config(admin: User = Depends(get_current_admin)):
    """Get system configuration (Admin only)"""
    try:
        config = {
            "platform_version": "1.0.0",
            "maintenance_mode": False,
            "features_enabled": {
                "audio": True,
                "offline": True,
                "collaboration": True,
                "api_access": True
            },
            "limits": {
                "max_questions_per_day_free": 20,
                "max_offline_banks_free": 0,
                "rate_limit_requests_per_minute": 60
            }
        }
        
        return {
            "success": True,
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Operation failed. Check server logs for details.")

@router.put("/config")
async def update_system_config(config_updates: Dict[str, Any] = Body(...), admin: User = Depends(get_current_admin)):
    """Update system configuration (Super Admin only)"""
    try:
        # TODO: Update configuration
        # TODO: Invalidate caches if needed
        
        return {
            "success": True,
            "message": "Configuration updated",
            "updated_keys": list(config_updates.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Operation failed. Check server logs for details.")

# AUDIT LOG ENDPOINTS

@router.get("/audit-log")
async def get_audit_log(
    action_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: int = Query(100),
    admin: User = Depends(get_current_admin),
):
    """Get audit log (Admin only)"""
    try:
        # TODO: Fetch from database
        
        logs = [
            {
                "id": "log_001",
                "timestamp": "2025-10-18T10:30:00",
                "admin_id": "admin_001",
                "admin_name": "John Admin",
                "action": "user_updated",
                "target_user_id": "user_123",
                "details": "Updated subscription tier",
                "ip_address": "192.168.1.1"
            }
        ]
        
        return {
            "success": True,
            "logs": logs,
            "total": len(logs)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Operation failed. Check server logs for details.")

