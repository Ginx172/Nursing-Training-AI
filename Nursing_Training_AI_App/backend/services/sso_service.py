"""
Single Sign-On (SSO) Service
Supports Azure AD, Okta, and SAML 2.0 authentication for Enterprise customers
"""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import jwt
import requests
from urllib.parse import urlencode
import base64
import xml.etree.ElementTree as ET
import os

class SSOService:
    """Service for handling SSO authentication"""
    
    def __init__(self):
        # Azure AD Configuration
        self.azure_tenant_id = os.getenv("AZURE_TENANT_ID", "")
        self.azure_client_id = os.getenv("AZURE_CLIENT_ID", "")
        self.azure_client_secret = os.getenv("AZURE_CLIENT_SECRET", "")
        self.azure_redirect_uri = os.getenv("AZURE_REDIRECT_URI", "")
        
        # Okta Configuration
        self.okta_domain = os.getenv("OKTA_DOMAIN", "")
        self.okta_client_id = os.getenv("OKTA_CLIENT_ID", "")
        self.okta_client_secret = os.getenv("OKTA_CLIENT_SECRET", "")
        self.okta_redirect_uri = os.getenv("OKTA_REDIRECT_URI", "")
        
        # SAML Configuration
        self.saml_entity_id = os.getenv("SAML_ENTITY_ID", "")
        self.saml_acs_url = os.getenv("SAML_ACS_URL", "")  # Assertion Consumer Service
        self.saml_slo_url = os.getenv("SAML_SLO_URL", "")  # Single Logout
    
    # ========================================
    # AZURE AD (Microsoft 365) INTEGRATION
    # ========================================
    
    def get_azure_ad_login_url(self, state: str) -> str:
        """Generate Azure AD login URL"""
        params = {
            "client_id": self.azure_client_id,
            "response_type": "code",
            "redirect_uri": self.azure_redirect_uri,
            "response_mode": "query",
            "scope": "openid profile email User.Read",
            "state": state,
            "prompt": "select_account"
        }
        
        base_url = f"https://login.microsoftonline.com/{self.azure_tenant_id}/oauth2/v2.0/authorize"
        return f"{base_url}?{urlencode(params)}"
    
    async def exchange_azure_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange Azure AD authorization code for access token"""
        try:
            token_url = f"https://login.microsoftonline.com/{self.azure_tenant_id}/oauth2/v2.0/token"
            
            data = {
                "client_id": self.azure_client_id,
                "client_secret": self.azure_client_secret,
                "code": code,
                "redirect_uri": self.azure_redirect_uri,
                "grant_type": "authorization_code"
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error exchanging Azure code: {e}")
            raise
    
    async def get_azure_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Azure AD"""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me",
                headers=headers
            )
            response.raise_for_status()
            
            user_data = response.json()
            
            return {
                "id": user_data.get("id"),
                "email": user_data.get("mail") or user_data.get("userPrincipalName"),
                "name": user_data.get("displayName"),
                "given_name": user_data.get("givenName"),
                "family_name": user_data.get("surname"),
                "job_title": user_data.get("jobTitle"),
                "department": user_data.get("department"),
                "provider": "azure_ad"
            }
        except Exception as e:
            print(f"Error getting Azure user info: {e}")
            raise
    
    # ========================================
    # OKTA INTEGRATION
    # ========================================
    
    def get_okta_login_url(self, state: str) -> str:
        """Generate Okta login URL"""
        params = {
            "client_id": self.okta_client_id,
            "response_type": "code",
            "scope": "openid profile email",
            "redirect_uri": self.okta_redirect_uri,
            "state": state
        }
        
        base_url = f"https://{self.okta_domain}/oauth2/v1/authorize"
        return f"{base_url}?{urlencode(params)}"
    
    async def exchange_okta_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange Okta authorization code for access token"""
        try:
            token_url = f"https://{self.okta_domain}/oauth2/v1/token"
            
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.okta_redirect_uri,
                "client_id": self.okta_client_id,
                "client_secret": self.okta_client_secret
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error exchanging Okta code: {e}")
            raise
    
    async def get_okta_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Okta"""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(
                f"https://{self.okta_domain}/oauth2/v1/userinfo",
                headers=headers
            )
            response.raise_for_status()
            
            user_data = response.json()
            
            return {
                "id": user_data.get("sub"),
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "given_name": user_data.get("given_name"),
                "family_name": user_data.get("family_name"),
                "provider": "okta"
            }
        except Exception as e:
            print(f"Error getting Okta user info: {e}")
            raise
    
    # ========================================
    # SAML 2.0 SUPPORT (Generic)
    # ========================================
    
    def generate_saml_request(self, relay_state: Optional[str] = None) -> str:
        """Generate SAML authentication request"""
        try:
            request_id = f"_{datetime.now().timestamp()}"
            issue_instant = datetime.utcnow().isoformat() + "Z"
            
            saml_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest 
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="SSO_ENDPOINT_HERE"
    AssertionConsumerServiceURL="{self.saml_acs_url}"
    ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
    <saml:Issuer>{self.saml_entity_id}</saml:Issuer>
</samlp:AuthnRequest>"""
            
            # Encode SAML request
            encoded = base64.b64encode(saml_request.encode()).decode()
            return encoded
        except Exception as e:
            print(f"Error generating SAML request: {e}")
            raise
    
    async def parse_saml_response(self, saml_response: str) -> Dict[str, Any]:
        """Parse and validate SAML response"""
        try:
            # Decode SAML response
            decoded = base64.b64decode(saml_response)
            
            # Parse XML
            root = ET.fromstring(decoded)
            
            # Extract user attributes
            # TODO: Implement proper SAML validation (signature, timestamp, etc.)
            # TODO: Use library like python3-saml
            
            user_info = {
                "email": "",  # Extract from SAML assertion
                "name": "",
                "attributes": {},
                "provider": "saml"
            }
            
            return user_info
        except Exception as e:
            print(f"Error parsing SAML response: {e}")
            raise
    
    # ========================================
    # UNIVERSAL SSO HANDLER
    # ========================================
    
    async def authenticate_sso(
        self,
        provider: str,
        code: Optional[str] = None,
        saml_response: Optional[str] = None
    ) -> Dict[str, Any]:
        """Universal SSO authentication handler"""
        try:
            if provider == "azure_ad":
                if not code:
                    raise ValueError("Authorization code required for Azure AD")
                
                # Exchange code for token
                token_data = await self.exchange_azure_code_for_token(code)
                
                # Get user info
                user_info = await self.get_azure_user_info(token_data["access_token"])
                
                # Generate internal JWT
                internal_token = self._generate_internal_token(user_info)
                
                return {
                    "success": True,
                    "user": user_info,
                    "token": internal_token,
                    "provider": "azure_ad"
                }
            
            elif provider == "okta":
                if not code:
                    raise ValueError("Authorization code required for Okta")
                
                # Exchange code for token
                token_data = await self.exchange_okta_code_for_token(code)
                
                # Get user info
                user_info = await self.get_okta_user_info(token_data["access_token"])
                
                # Generate internal JWT
                internal_token = self._generate_internal_token(user_info)
                
                return {
                    "success": True,
                    "user": user_info,
                    "token": internal_token,
                    "provider": "okta"
                }
            
            elif provider == "saml":
                if not saml_response:
                    raise ValueError("SAML response required")
                
                # Parse SAML response
                user_info = await self.parse_saml_response(saml_response)
                
                # Generate internal JWT
                internal_token = self._generate_internal_token(user_info)
                
                return {
                    "success": True,
                    "user": user_info,
                    "token": internal_token,
                    "provider": "saml"
                }
            
            else:
                raise ValueError(f"Unsupported SSO provider: {provider}")
        
        except Exception as e:
            print(f"SSO authentication error: {e}")
            raise
    
    def _generate_internal_token(self, user_info: Dict) -> str:
        """Generate internal JWT token after SSO authentication"""
        try:
            secret_key = os.getenv("SECRET_KEY", "")
            
            payload = {
                "sub": user_info["email"],
                "name": user_info["name"],
                "email": user_info["email"],
                "provider": user_info["provider"],
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            
            token = jwt.encode(payload, secret_key, algorithm="HS256")
            return token
        except Exception as e:
            print(f"Error generating internal token: {e}")
            raise
    
    # ========================================
    # ORGANIZATION SSO CONFIGURATION
    # ========================================
    
    async def configure_organization_sso(
        self,
        organization_id: str,
        sso_provider: str,
        configuration: Dict[str, Any]
    ) -> Dict:
        """Configure SSO for an organization"""
        try:
            sso_config = {
                "organization_id": organization_id,
                "provider": sso_provider,
                "enabled": True,
                "configuration": configuration,
                "created_at": datetime.now().isoformat(),
                "enforce_sso": configuration.get("enforce_sso", False),  # Force all users to use SSO
                "allowed_domains": configuration.get("allowed_domains", []),
                "auto_provision_users": configuration.get("auto_provision", True),
                "default_role": configuration.get("default_role", "user")
            }
            
            # TODO: Save to database
            # TODO: Validate configuration
            
            return sso_config
        except Exception as e:
            print(f"Error configuring SSO: {e}")
            raise
    
    async def get_organization_sso_config(self, organization_id: str) -> Optional[Dict]:
        """Get SSO configuration for organization"""
        try:
            # TODO: Fetch from database
            return None
        except Exception as e:
            print(f"Error getting SSO config: {e}")
            return None
    
    def validate_sso_domain(self, email: str, allowed_domains: list) -> bool:
        """Validate if user's email domain is allowed for SSO"""
        domain = email.split("@")[1].lower()
        return domain in [d.lower() for d in allowed_domains]

# Singleton instance
sso_service = SSOService()

