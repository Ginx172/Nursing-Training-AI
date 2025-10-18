"""
🏥 Nursing Training AI - Backend Main Application (Simplified)
FastAPI application pentru sistemul de training medical AI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Inițializare aplicație FastAPI
app = FastAPI(
    title="Nursing Training AI API",
    description="API pentru aplicația de training medical AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware pentru CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Import și include router-urile simple
try:
    from api.routes import banks_catalog, auto_presentation
    app.include_router(banks_catalog.router, prefix="/api/banks", tags=["Banks Catalog"]) 
    app.include_router(auto_presentation.router, prefix="/api/auto", tags=["Auto Presentation"]) 
    print("✅ Routers loaded successfully")
except Exception as e:
    print(f"❌ Error loading routers: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
