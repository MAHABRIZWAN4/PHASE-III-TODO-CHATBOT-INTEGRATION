"""Vercel serverless function entry point for FastAPI."""

import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import FastAPI app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routes
from routes.auth import router as auth_router
from routes.tasks import router as tasks_router

try:
    from routes.chat import router as chat_router
    CHAT_AVAILABLE = True
except ImportError as e:
    print(f"Chat router not available: {e}")
    CHAT_AVAILABLE = False

# Create FastAPI app
app = FastAPI(
    title="Todo API",
    description="Backend API for Phase II Todo Web Application",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://frontend-kappa-ruddy-34.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)

if CHAT_AVAILABLE:
    app.include_router(chat_router)

@app.get("/")
async def root():
    return {"message": "Todo API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
