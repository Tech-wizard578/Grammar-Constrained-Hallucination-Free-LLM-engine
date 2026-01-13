"""FastAPI main application for Hallucination-Free Engine."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import routes
from api.routes import query, documents, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    print("🚀 Starting Hallucination-Free Engine API...")
    yield
    # Shutdown
    print("👋 Shutting down API...")


# Create FastAPI app
app = FastAPI(
    title="Hallucination-Free LLM Engine",
    description="Grammar-constrained RAG system with citation tracking",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(documents.router, prefix="/api", tags=["Documents"])
app.include_router(stats.router, prefix="/api", tags=["Stats"])


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "Hallucination-Free LLM Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
