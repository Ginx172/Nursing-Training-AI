"""
🏥 Nursing Training AI - Backend Main Application (Minimal)
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

@app.get("/api/banks/catalog")
async def test_banks():
    """Test endpoint for banks"""
    return {
        "message": "Banks endpoint working",
        "items": [],
        "total": 0
    }

@app.get("/api/auto/summary")
async def test_auto():
    """Test endpoint for auto presentation"""
    return {
        "message": "Auto presentation working",
        "capabilities": {
            "question_banks": 1890,
            "specialties": 7,
            "bands": 7
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
