"""API models for the Hallucination-Free Engine web interface."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ============ REQUEST MODELS ============

class QueryRequest(BaseModel):
    """Request body for query endpoint."""
    question: str = Field(..., min_length=5, max_length=1000, description="Question to answer")
    verbose: bool = Field(default=False, description="Include detailed logging")


class IngestRequest(BaseModel):
    """Request body for document ingestion."""
    urls: List[str] = Field(default=[], description="URLs to scrape and index")
    files: List[str] = Field(default=[], description="File paths to index")


# ============ RESPONSE MODELS ============

class CitationResponse(BaseModel):
    """Citation in the response."""
    source_id: int
    quote: str
    relevance_score: float


class QueryResponse(BaseModel):
    """Response from query endpoint."""
    success: bool
    answer: Optional[str] = None
    reasoning: Optional[str] = None
    confidence: Optional[str] = None
    citations: List[CitationResponse] = []
    elapsed_time_seconds: float = 0.0
    iterations: int = 0
    documents_retrieved: int = 0
    errors: List[str] = []


class StatsResponse(BaseModel):
    """Knowledge base statistics."""
    collection_name: str
    total_documents: int
    embedding_model: str
    chunk_size: int
    chunk_overlap: int


class IngestResponse(BaseModel):
    """Response from document ingestion."""
    success: bool
    chunks_indexed: int = 0
    message: str = ""


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
