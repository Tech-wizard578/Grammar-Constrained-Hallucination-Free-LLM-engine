"""Statistics route for Hallucination-Free Engine API."""

from fastapi import APIRouter
from api.models import StatsResponse

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get knowledge base statistics.
    
    Returns document count, embedding model, and chunk configuration.
    """
    try:
        from retriever import HybridRetriever
        
        retriever = HybridRetriever()
        stats = retriever.get_stats()
        
        return StatsResponse(**stats)
        
    except Exception as e:
        # Return default stats on error
        return StatsResponse(
            collection_name="unknown",
            total_documents=0,
            embedding_model="unknown",
            chunk_size=0,
            chunk_overlap=0
        )
