"""
🏥 Nursing Training AI - Backend Main Application
FastAPI application pentru sistemul de training medical AI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import os
from contextlib import asynccontextmanager

from api.routes import auth, users, training, demo, bands, questions, security as security_routes, security_monitoring, banks_catalog, audio, auto_presentation, ai_services
from core.security import SecurityHeadersMiddleware, RateLimiterMiddleware
from core.advanced_security import advanced_security_middleware
from core.database import init_db
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events pentru aplicație"""
    # Startup
    print("🚀 Starting Nursing Training AI Backend...")
    await init_db()
    print("✅ Database initialized")
    
    # Inițializează serviciile AI
    print("🤖 Initializing AI Services...")
    from services.ai_integration_service import ai_integration_service
    await ai_integration_service.initialize()
    print("✅ AI Services initialized")
    
    yield
    # Shutdown
    print("🛑 Shutting down Nursing Training AI Backend...")


# Inițializare aplicație FastAPI
app = FastAPI(
    title="Nursing Training AI API",
    description="API pentru aplicația de training medical AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware pentru CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware pentru trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts_list
)

# Advanced Security middlewares (order matters!)
app.add_middleware(advanced_security_middleware.__class__)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimiterMiddleware, requests_per_minute=60)  # Reduced for max security

# Include router-urile
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(training.router, prefix="/api/training", tags=["Training"])
app.include_router(demo.router, prefix="/api/demo", tags=["Demo"])
app.include_router(bands.router, prefix="/api/bands", tags=["Bands"])
app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])
app.include_router(security_routes.router, prefix="/api/security", tags=["Security"])
app.include_router(security_monitoring.router, prefix="/api/security", tags=["Security Monitoring"])
app.include_router(banks_catalog.router, prefix="/api/banks", tags=["Banks Catalog"]) 
app.include_router(audio.router, prefix="/api/audio", tags=["Audio"]) 
app.include_router(auto_presentation.router, prefix="/api/auto", tags=["Auto Presentation"])
app.include_router(ai_services.router, prefix="/api/ai", tags=["AI Services"]) 


@app.get("/")
async def root():
    """Endpoint de bază pentru verificarea statusului"""
    return {
        "message": "🏥 Nursing Training AI API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "services": {
            "rag": "active",
            "mcp": "active",
            "ai": "active"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
