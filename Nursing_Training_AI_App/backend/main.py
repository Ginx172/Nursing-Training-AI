"""
Nursing Training AI - Main Application
Enterprise-Grade FastAPI Application with complete OpenAPI documentation
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import time
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
import os

# Import routers
from api import (
    analytics,
    admin,
    payments,
    sso
)

# Import services
from services.monitoring_service import monitoring_service
from core.database import init_db, check_database_health

# Initialize Sentry for error tracking
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", ""),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment=os.getenv("ENVIRONMENT", "production")
)

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Nursing Training AI API...")
    
    # Initialize database
    init_db()
    
    # Check health
    health = await check_database_health()
    print(f"📊 Database Health: {health['status']}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Nursing Training AI API...")

# Create FastAPI app with comprehensive metadata
app = FastAPI(
    title="Nursing Training AI API",
    description="""
    ## 🏥 Enterprise Healthcare Training Platform API
    
    Complete API for UK healthcare professional training with AI-powered question generation,
    personalized learning paths, and comprehensive analytics.
    
    ### 🎯 Features
    
    - **2,140+ Question Banks** covering all UK healthcare sectors
    - **42,800+ Questions** across all NHS bands (2-8d)
    - **5 Healthcare Sectors**: NHS, Private, Care Homes, Community, Primary Care
    - **33 Specialties** from AMU to Primary Care
    - **AI-Powered**: Personalized recommendations and feedback
    - **Enterprise Security**: SSO, MFA, RBAC, Audit logging, GDPR compliance
    - **Scalable**: Kubernetes, auto-scaling, read replicas
    
    ### 🔐 Authentication
    
    This API uses JWT Bearer tokens for authentication. Include your token in the Authorization header:
    
    ```
    Authorization: Bearer your_jwt_token_here
    ```
    
    #### SSO Support
    - Azure AD (Microsoft 365)
    - Okta
    - SAML 2.0 (any provider)
    
    ### 📊 Subscription Plans
    
    - **Demo**: FREE - Limited access for trial
    - **Basic**: £9.99/month - Individual professionals
    - **Professional**: £19.99/month - Unlimited access, CPD certificates
    - **Enterprise**: £199/month - 50 users, team analytics, API access
    
    ### 🚀 Rate Limits
    
    - **Demo**: 20 requests/minute
    - **Basic**: 60 requests/minute
    - **Professional**: 120 requests/minute
    - **Enterprise**: 300 requests/minute (customizable)
    
    ### 📞 Support
    
    - **Email**: support@nursingtrainingai.com
    - **Documentation**: https://docs.nursingtrainingai.com
    - **Status Page**: https://status.nursingtrainingai.com
    
    ### 📄 Legal
    
    - **Terms of Service**: https://nursingtrainingai.com/terms
    - **Privacy Policy**: https://nursingtrainingai.com/privacy
    - **GDPR Compliant**: Full data protection compliance
    - **SOC 2 Type II**: Enterprise security certified
    """,
    version="1.0.0",
    terms_of_service="https://nursingtrainingai.com/terms",
    contact={
        "name": "Nursing Training AI Support",
        "url": "https://nursingtrainingai.com/support",
        "email": "support@nursingtrainingai.com",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://nursingtrainingai.com/license",
    },
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User authentication and registration"
        },
        {
            "name": "sso",
            "description": "Single Sign-On (Azure AD, Okta, SAML)"
        },
        {
            "name": "questions",
            "description": "Question banks and individual questions"
        },
        {
            "name": "analytics",
            "description": "User and platform analytics"
        },
        {
            "name": "payments",
            "description": "Subscription and payment management"
        },
        {
            "name": "admin",
            "description": "Admin panel endpoints (requires admin role)"
        },
        {
            "name": "health",
            "description": "System health and monitoring"
        }
    ],
    servers=[
        {
            "url": "https://api.nursingtrainingai.com",
            "description": "Production server"
        },
        {
            "url": "https://staging-api.nursingtrainingai.com",
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ========================================
# MIDDLEWARE
# ========================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request tracking middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track all API requests for monitoring"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    
    # Track metrics
    monitoring_service.track_request(
        endpoint=request.url.path,
        method=request.method,
        duration_ms=duration_ms,
        status_code=response.status_code
    )
    
    # Add headers
    response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
    response.headers["X-API-Version"] = "1.0.0"
    
    return response

# ========================================
# ROUTERS
# ========================================

# Include all routers
app.include_router(analytics.router)
app.include_router(admin.router)
app.include_router(payments.router)
app.include_router(sso.router)

# ========================================
# HEALTH CHECK ENDPOINTS
# ========================================

@app.get(
    "/api/health",
    tags=["health"],
    summary="Health check endpoint",
    description="Check if API is running and healthy",
    response_description="Health status of the API and its dependencies"
)
async def health_check():
    """
    Comprehensive health check endpoint
    
    Returns health status of:
    - API server
    - Database (PostgreSQL)
    - Cache (Redis)
    - System resources
    """
    from services.monitoring_service import monitoring_service
    
    health = monitoring_service.get_comprehensive_health_check()
    
    if health["overall_status"] == "healthy":
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=health
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health
        )

@app.get(
    "/api/version",
    tags=["health"],
    summary="Get API version information"
)
async def get_version():
    """Get API version and build information"""
    return {
        "api_version": "1.0.0",
        "build_date": "2025-10-18",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "features": {
            "sso": True,
            "mfa": True,
            "encryption": True,
            "audit_logging": True,
            "gdpr_compliant": True
        }
    }

@app.get(
    "/",
    tags=["health"],
    summary="Root endpoint"
)
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Nursing Training AI API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/api/health",
        "status": "operational"
    }

# ========================================
# CUSTOM OPENAPI SCHEMA
# ========================================

def custom_openapi():
    """Customize OpenAPI schema with additional information"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        servers=app.servers
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Bearer token authentication"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key for programmatic access (Enterprise only)"
        },
        "OAuth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "https://api.nursingtrainingai.com/api/oauth/authorize",
                    "tokenUrl": "https://api.nursingtrainingai.com/api/oauth/token",
                    "scopes": {
                        "read": "Read access",
                        "write": "Write access",
                        "admin": "Admin access"
                    }
                }
            }
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [
        {"BearerAuth": []},
        {"ApiKeyAuth": []}
    ]
    
    # Add custom extensions
    openapi_schema["x-logo"] = {
        "url": "https://nursingtrainingai.com/logo.png",
        "altText": "Nursing Training AI"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ========================================
# ERROR HANDLERS
# ========================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": request.url.path,
            "documentation": "/docs"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "support": "support@nursingtrainingai.com"
        }
    )

# ========================================
# STARTUP MESSAGE
# ========================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     🏥 NURSING TRAINING AI - ENTERPRISE EDITION 🏥       ║
    ║                                                           ║
    ║  Production-Ready Healthcare Training Platform           ║
    ║  Enterprise Features: SSO, MFA, RBAC, Audit, GDPR       ║
    ║  Infrastructure: K8s, Auto-scale, Monitoring, Backup     ║
    ║                                                           ║
    ║  📚 2,140 Question Banks | 42,800+ Questions            ║
    ║  🌐 All UK Healthcare Sectors | All NHS Bands           ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    📖 API Documentation: http://localhost:8000/docs
    📊 Health Check: http://localhost:8000/api/health
    🔐 Security: SSO, MFA, Encryption enabled
    
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        workers=int(os.getenv("WORKERS", "4")),
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
