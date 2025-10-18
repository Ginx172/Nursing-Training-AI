"""
Multi-Tenancy Service
Implements secure tenant isolation for Enterprise organizations
Strategy: Schema-per-tenant for maximum isolation and security
"""

from typing import Optional, Dict, Any, List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from datetime import datetime
import os

from core.database import primary_engine, Base
from services.audit_service import audit_service, AuditAction, AuditSeverity

class TenantManager:
    """Manages tenant creation, isolation, and lifecycle"""
    
    def __init__(self):
        self.default_schema = "public"
        self.tenant_schemas = {}  # Cache of tenant schemas
    
    # ========================================
    # TENANT CREATION
    # ========================================
    
    async def create_tenant(
        self,
        organization_id: str,
        organization_name: str,
        owner_email: str,
        subscription_tier: str
    ) -> Dict:
        """
        Create new tenant with isolated schema
        
        Each organization gets:
        - Dedicated database schema
        - Isolated data storage
        - Separate resource quotas
        - Custom configuration
        """
        try:
            # Generate schema name (sanitized)
            schema_name = f"tenant_{organization_id}".lower().replace("-", "_")
            
            # Create schema in database
            with primary_engine.connect() as conn:
                # Create schema
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
                
                # Grant permissions
                conn.execute(text(f"""
                    GRANT ALL ON SCHEMA {schema_name} TO nursing_user;
                    GRANT ALL ON ALL TABLES IN SCHEMA {schema_name} TO nursing_user;
                    ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} 
                    GRANT ALL ON TABLES TO nursing_user;
                """))
                
                conn.commit()
            
            # Create tenant metadata
            tenant = {
                "id": organization_id,
                "name": organization_name,
                "schema_name": schema_name,
                "owner_email": owner_email,
                "subscription_tier": subscription_tier,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "settings": {
                    "max_users": self._get_max_users_for_tier(subscription_tier),
                    "features_enabled": self._get_features_for_tier(subscription_tier),
                    "storage_quota_gb": self._get_storage_quota(subscription_tier),
                    "api_rate_limit": self._get_rate_limit(subscription_tier)
                },
                "branding": {
                    "logo_url": None,
                    "primary_color": "#0066CC",
                    "custom_domain": None
                }
            }
            
            # Initialize tenant schema with tables
            await self._initialize_tenant_schema(schema_name)
            
            # Save tenant metadata to public schema
            # TODO: Save to tenants table in public schema
            
            # Cache schema
            self.tenant_schemas[organization_id] = schema_name
            
            # Audit log
            await audit_service.log(
                action=AuditAction.ORG_CREATED,
                organization_id=organization_id,
                details={"schema_name": schema_name, "tier": subscription_tier},
                severity=AuditSeverity.INFO
            )
            
            return tenant
        except Exception as e:
            print(f"Error creating tenant: {e}")
            raise
    
    async def _initialize_tenant_schema(self, schema_name: str):
        """Create all tables in tenant schema"""
        try:
            # Set search path to tenant schema
            with primary_engine.connect() as conn:
                conn.execute(text(f"SET search_path TO {schema_name}"))
                
                # Create all tables in this schema
                Base.metadata.create_all(bind=primary_engine)
                
                conn.commit()
            
            print(f"✅ Tenant schema {schema_name} initialized")
        except Exception as e:
            print(f"Error initializing tenant schema: {e}")
            raise
    
    # ========================================
    # TENANT ACCESS & ROUTING
    # ========================================
    
    def get_tenant_schema(self, organization_id: str) -> str:
        """Get schema name for organization"""
        # Check cache
        if organization_id in self.tenant_schemas:
            return self.tenant_schemas[organization_id]
        
        # TODO: Fetch from database
        schema_name = f"tenant_{organization_id}".lower().replace("-", "_")
        self.tenant_schemas[organization_id] = schema_name
        
        return schema_name
    
    def set_tenant_context(self, db: Session, organization_id: str):
        """Set database context to tenant schema"""
        try:
            schema_name = self.get_tenant_schema(organization_id)
            
            # Set search path to tenant schema
            db.execute(text(f"SET search_path TO {schema_name}"))
            
        except Exception as e:
            print(f"Error setting tenant context: {e}")
            raise
    
    # ========================================
    # TENANT MANAGEMENT
    # ========================================
    
    async def update_tenant(
        self,
        organization_id: str,
        updates: Dict[str, Any]
    ) -> Dict:
        """Update tenant configuration"""
        try:
            # TODO: Update tenant metadata in database
            
            # Audit log
            await audit_service.log(
                action=AuditAction.ORG_UPDATED,
                organization_id=organization_id,
                details={"updates": updates},
                severity=AuditSeverity.INFO
            )
            
            return {"success": True}
        except Exception as e:
            print(f"Error updating tenant: {e}")
            raise
    
    async def delete_tenant(
        self,
        organization_id: str,
        confirm: bool = False
    ) -> Dict:
        """
        Delete tenant and all associated data
        WARNING: This is irreversible!
        """
        try:
            if not confirm:
                raise ValueError("Must confirm deletion with confirm=True")
            
            schema_name = self.get_tenant_schema(organization_id)
            
            # Drop schema (CASCADE drops all tables)
            with primary_engine.connect() as conn:
                conn.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
                conn.commit()
            
            # Remove from cache
            self.tenant_schemas.pop(organization_id, None)
            
            # TODO: Delete tenant metadata
            # TODO: Cancel Stripe subscription
            
            # Audit log
            await audit_service.log(
                action=AuditAction.ORG_DELETED,
                organization_id=organization_id,
                details={"schema_name": schema_name},
                severity=AuditSeverity.CRITICAL
            )
            
            return {
                "success": True,
                "message": f"Tenant {organization_id} deleted",
                "deleted_schema": schema_name
            }
        except Exception as e:
            print(f"Error deleting tenant: {e}")
            raise
    
    # ========================================
    # RESOURCE QUOTAS PER TIER
    # ========================================
    
    def _get_max_users_for_tier(self, tier: str) -> int:
        """Get max users based on subscription tier"""
        quotas = {
            "demo": 1,
            "basic": 1,
            "professional": 1,
            "enterprise": 50
        }
        return quotas.get(tier, 1)
    
    def _get_features_for_tier(self, tier: str) -> List[str]:
        """Get enabled features for tier"""
        from config.stripe_config import SUBSCRIPTION_PLANS, SubscriptionTier
        plan = SUBSCRIPTION_PLANS.get(SubscriptionTier(tier), {})
        return list(plan.get("features", {}).keys())
    
    def _get_storage_quota(self, tier: str) -> int:
        """Get storage quota in GB"""
        quotas = {
            "demo": 1,
            "basic": 5,
            "professional": 20,
            "enterprise": 100
        }
        return quotas.get(tier, 1)
    
    def _get_rate_limit(self, tier: str) -> int:
        """Get API rate limit (requests per minute)"""
        limits = {
            "demo": 20,
            "basic": 60,
            "professional": 120,
            "enterprise": 300
        }
        return limits.get(tier, 20)
    
    # ========================================
    # TENANT METRICS
    # ========================================
    
    async def get_tenant_usage(self, organization_id: str) -> Dict:
        """Get tenant resource usage"""
        try:
            schema_name = self.get_tenant_schema(organization_id)
            
            # Get storage usage
            with primary_engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                    FROM pg_tables
                    WHERE schemaname = '{schema_name}'
                """))
                
                total_size = sum([row[0] for row in result], 0)
            
            # TODO: Get other metrics from database
            
            usage = {
                "organization_id": organization_id,
                "schema_name": schema_name,
                "storage_used_gb": 0,  # TODO: Calculate from total_size
                "users_count": 0,  # TODO: Count from users table
                "api_requests_today": 0,  # TODO: From metrics
                "questions_answered_total": 0  # TODO: From answers table
            }
            
            return usage
        except Exception as e:
            print(f"Error getting tenant usage: {e}")
            raise

# Singleton instance
tenant_manager = TenantManager()

# ========================================
# TENANT CONTEXT MIDDLEWARE
# ========================================

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to set tenant context for each request"""
    
    async def dispatch(self, request: Request, call_next):
        # Extract organization_id from request
        # Could be from: subdomain, header, JWT token, etc.
        
        organization_id = None
        
        # Option 1: From subdomain (org1.nursingtrainingai.com)
        host = request.headers.get("host", "")
        if "." in host:
            subdomain = host.split(".")[0]
            if subdomain not in ["www", "api", "app"]:
                organization_id = subdomain
        
        # Option 2: From header
        if not organization_id:
            organization_id = request.headers.get("X-Organization-ID")
        
        # Option 3: From JWT token
        # TODO: Extract from decoded JWT
        
        # Store in request state
        request.state.organization_id = organization_id
        request.state.tenant_schema = (
            tenant_manager.get_tenant_schema(organization_id)
            if organization_id else "public"
        )
        
        response = await call_next(request)
        return response

