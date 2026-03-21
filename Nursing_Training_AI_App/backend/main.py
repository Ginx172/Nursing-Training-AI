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

from core.config import settings

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
    traces_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
    environment=settings.ENVIRONMENT
)

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Nursing Training AI API...")
    init_db()
    health = await check_database_health()
    print(f"Database Health: {health['status']}")
    yield
    print("Shutting down Nursing Training AI API...")

# Create FastAPI app
app = FastAPI(
    title="Nursing Training AI API",
    description="""
    Enterprise Healthcare Training Platform API

    Complete API for UK healthcare professional training with AI-powered
    question generation, personalized learning paths, and analytics.

    Features:
    - 2,140+ Question Banks covering all UK healthcare sectors
    - 42,800+ Questions across all NHS bands (2-8d)
    - 5 Healthcare Sectors: NHS, Private, Care Homes, Community, Primary Care
    - 33 Specialties from AMU to Primary Care
    - Enterprise Security: SSO, MFA, RBAC, Audit logging, GDPR compliance
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
        {"name": "authentication", "description": "User authentication and registration"},
        {"name": "sso", "description": "Single Sign-On (Azure AD, Okta, SAML)"},
        {"name": "questions", "description": "Question banks and individual questions"},
        {"name": "analytics", "description": "User and platform analytics"},
        {"name": "payments", "description": "Subscription and payment management"},
        {"name": "admin", "description": "Admin panel endpoints (requires admin role)"},
        {"name": "health", "description": "System health and monitoring"},
    ],
    servers=[
        {"url": "https://api.nursingtrainingai.com", "description": "Production server"},
        {"url": "https://staging-api.nursingtrainingai.com", "description": "Staging server"},
        {"url": "http://localhost:8000", "description": "Development server"},
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ========================================
# MIDDLEWARE
# ========================================

# CORS - uses validated origins from config.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-API-Key",
        "X-Organization-ID",
    ],
)

# GZIP Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security Headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Request tracking middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    monitoring_service.track_request(
        endpoint=request.url.path,
        method=request.method,
        duration_ms=duration_ms,
        status_code=response.status_code
    )
    response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
    response.headers["X-API-Version"] = "1.0.0"
    return response

# ========================================
# ROUTERS
# ========================================

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
    Comprehensive health check endpoint.
    Returns health status of API server, Database, Cache, System resources.
    """
    from services.monitoring_service import monitoring_service
    health = monitoring_service.get_comprehensive_health_check()
    if health["overall_status"] == "healthy":
        return JSONResponse(status_code=status.HTTP_200_OK, content=health)
    else:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=health)

@app.get("/api/version", tags=["health"], summary="Get API version information")
async def get_version():
    return {
        "api_version": "1.0.0",
        "build_date": "2025-10-18",
        "environment": settings.ENVIRONMENT,
        "features": {
            "sso": True,
            "mfa": True,
            "encryption": True,
            "audit_logging": True,
            "gdpr_compliant": True
        }
    }

@app.get("/", tags=["health"], summary="Root endpoint")
async def root():
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
    }
    openapi_schema["security"] = [
        {"BearerAuth": []},
        {"ApiKeyAuth": []}
    ]
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
# STARTUP
# ========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        workers=int(os.getenv("WORKERS", "4")),
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
