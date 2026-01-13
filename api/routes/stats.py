"""Statistics route for Hallucination-Free Engine API."""

from fastapi import APIRouter
from api.models import StatsResponse
import os

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get knowledge base statistics.
    
    Returns document count, embedding model, and chunk configuration.
    Uses lightweight ChromaDB client to avoid loading heavy embedding models.
    """
    try:
        import chromadb
        from config import config
        
        # Use lightweight persistent client without loading embeddings
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db")
        
        # Check if chroma_db exists
        if not os.path.exists(db_path):
            return StatsResponse(
                collection_name="knowledge_base",
                total_documents=0,
                embedding_model=config.EMBEDDING_MODEL,
                chunk_size=config.CHUNK_SIZE,
                chunk_overlap=config.CHUNK_OVERLAP
            )
        
        client = chromadb.PersistentClient(path=db_path)
        
        try:
            collection = client.get_collection("knowledge_base")
            doc_count = collection.count()
        except Exception:
            doc_count = 0
        
        return StatsResponse(
            collection_name="knowledge_base",
            total_documents=doc_count,
            embedding_model=config.EMBEDDING_MODEL,
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        
    except Exception as e:
        # Return default stats on error
        return StatsResponse(
            collection_name="knowledge_base",
            total_documents=0,
            embedding_model="all-MiniLM-L6-v2",
            chunk_size=500,
            chunk_overlap=50
        )
