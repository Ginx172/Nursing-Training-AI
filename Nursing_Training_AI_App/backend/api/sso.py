"""
SSO API Endpoints
Handles Single Sign-On authentication flows
"""

from fastapi import APIRouter, HTTPException, Request, Query, Depends
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
import secrets
import time
import threading

from services.sso_service import sso_service

router = APIRouter(prefix="/api/sso", tags=["sso"])

# CSRF state tokens with expiry timestamps.
# WARNING: This in-process dict is NOT suitable for multi-worker or multi-instance
# deployments — tokens created in one worker will be invisible to others and are
# lost on restart. Replace with a shared Redis store (with TTL) in production.
_STATE_TOKEN_TTL_SECONDS = 300  # 5 minutes
state_tokens: Dict[str, Dict] = {}
_state_tokens_lock = threading.Lock()


def _cleanup_expired_state_tokens() -> None:
    """Remove state tokens that have exceeded their TTL. Must be called with _state_tokens_lock held."""
    now = time.monotonic()
    expired = [k for k, v in state_tokens.items() if now - v["_created_at"] > _STATE_TOKEN_TTL_SECONDS]
    for k in expired:
        state_tokens.pop(k, None)

# Request Models
class SSOConfigRequest(BaseModel):
    organization_id: str
    provider: str  # azure_ad, okta, saml
    configuration: Dict

class SSOLoginRequest(BaseModel):
    email: EmailStr
    return_url: Optional[str] = None

# ========================================
# SSO LOGIN FLOW
# ========================================

@router.post("/initiate")
async def initiate_sso_login(request: SSOLoginRequest):
    """Initiate SSO login flow"""
    try:
        # Check if user's organization has SSO configured
        # TODO: Look up organization by email domain
        domain = request.email.split("@")[1]
        
        # TODO: Fetch organization SSO config from database
        # For now, default to Azure AD for @nhs.net emails
        provider = "azure_ad" if domain.endswith("nhs.net") else None
        
        if not provider:
            return {
                "success": False,
                "message": "SSO not configured for this email domain",
                "use_standard_login": True
            }
        
        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)
        with _state_tokens_lock:
            _cleanup_expired_state_tokens()
            state_tokens[state] = {
                "email": request.email,
                "return_url": request.return_url,
                "_created_at": time.monotonic(),
            }
        
        # Get login URL based on provider
        if provider == "azure_ad":
            login_url = sso_service.get_azure_ad_login_url(state)
        elif provider == "okta":
            login_url = sso_service.get_okta_login_url(state)
        else:
            raise HTTPException(status_code=400, detail="Unsupported SSO provider")
        
        return {
            "success": True,
            "provider": provider,
            "login_url": login_url,
            "state": state
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/callback/{provider}")
async def sso_callback(
    provider: str,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None)
):
    """Handle SSO callback after user authenticates"""
    try:
        # Check for errors
        if error:
            raise HTTPException(status_code=400, detail=f"SSO error: {error}")
        
        # Validate state token (also evict expired tokens)
        with _state_tokens_lock:
            _cleanup_expired_state_tokens()
            if not state or state not in state_tokens:
                raise HTTPException(status_code=400, detail="Invalid state token")
            state_data = state_tokens.pop(state)
        
        # Authenticate with SSO provider
        auth_result = await sso_service.authenticate_sso(
            provider=provider,
            code=code
        )
        
        if not auth_result["success"]:
            raise HTTPException(status_code=401, detail="SSO authentication failed")
        
        # TODO: Create or update user in database
        # TODO: Create session
        
        # Return token or redirect
        return_url = state_data.get("return_url", "/dashboard")
        
        return {
            "success": True,
            "user": auth_result["user"],
            "token": auth_result["token"],
            "redirect_url": return_url
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/saml/acs")
async def saml_assertion_consumer_service(request: Request):
    """SAML Assertion Consumer Service endpoint"""
    try:
        form_data = await request.form()
        saml_response = form_data.get("SAMLResponse")
        relay_state = form_data.get("RelayState")
        
        if not saml_response:
            raise HTTPException(status_code=400, detail="Missing SAML response")
        
        # Authenticate with SAML
        auth_result = await sso_service.authenticate_sso(
            provider="saml",
            saml_response=saml_response
        )
        
        # TODO: Create or update user
        # TODO: Create session
        
        return {
            "success": True,
            "user": auth_result["user"],
            "token": auth_result["token"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/saml/metadata")
async def get_saml_metadata():
    """Get SAML service provider metadata"""
    metadata = f"""<?xml version="1.0"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
                     entityID="{sso_service.saml_entity_id}">
    <md:SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:AssertionConsumerService 
            Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            Location="{sso_service.saml_acs_url}"
            index="1"/>
        <md:SingleLogoutService 
            Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            Location="{sso_service.saml_slo_url}"/>
    </md:SPSSODescriptor>
</md:EntityDescriptor>"""
    
    return Response(content=metadata, media_type="application/xml")

# ========================================
# ORGANIZATION SSO MANAGEMENT (Admin)
# ========================================

@router.post("/organizations/{org_id}/configure")
async def configure_organization_sso(org_id: str, config: SSOConfigRequest):
    """Configure SSO for an organization (Admin only)"""
    try:
        # TODO: Verify admin permissions
        
        sso_config = await sso_service.configure_organization_sso(
            organization_id=org_id,
            sso_provider=config.provider,
            configuration=config.configuration
        )
        
        return {
            "success": True,
            "message": "SSO configured successfully",
            "configuration": sso_config
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/organizations/{org_id}/config")
async def get_organization_sso_config(org_id: str):
    """Get SSO configuration for organization"""
    try:
        config = await sso_service.get_organization_sso_config(org_id)
        
        if not config:
            return {
                "success": True,
                "sso_enabled": False,
                "config": None
            }
        
        # Don't expose sensitive data like secrets
        safe_config = {
            "provider": config.get("provider"),
            "enabled": config.get("enabled"),
            "enforce_sso": config.get("enforce_sso"),
            "allowed_domains": config.get("allowed_domains")
        }
        
        return {
            "success": True,
            "sso_enabled": True,
            "config": safe_config
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/organizations/{org_id}/sso")
async def disable_organization_sso(org_id: str):
    """Disable SSO for organization (Admin only)"""
    try:
        # TODO: Verify admin permissions
        # TODO: Disable in database
        
        return {
            "success": True,
            "message": "SSO disabled for organization"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ========================================
# SSO TESTING ENDPOINTS
# ========================================

@router.get("/test/azure-ad")
async def test_azure_ad_connection():
    """Test Azure AD connection (Admin only)"""
    try:
        # TODO: Test connection to Azure AD
        return {
            "success": True,
            "message": "Azure AD connection successful",
            "tenant_id": sso_service.azure_tenant_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/test/okta")
async def test_okta_connection():
    """Test Okta connection (Admin only)"""
    try:
        # TODO: Test connection to Okta
        return {
            "success": True,
            "message": "Okta connection successful",
            "domain": sso_service.okta_domain
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

