"""Main FastAPI application for Todo Web App."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import init_db
from routes.auth import router as auth_router
from routes.tasks import router as tasks_router
from routes.chat import router as chat_router

app = FastAPI(
    title="Todo API",
    description="Backend API for Phase II Todo Web Application",
    version="1.0.0",
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://*.pythonanywhere.com",
        "https://frontend-kappa-ruddy-34.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure tables exist for local dev
@app.on_event("startup")
async def on_startup():
    await init_db()


# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "Todo API is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
