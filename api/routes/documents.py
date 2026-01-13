"""Document management route for Hallucination-Free Engine API."""

from fastapi import APIRouter, HTTPException
from api.models import IngestRequest, IngestResponse, ErrorResponse

router = APIRouter()


@router.post("/documents/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """
    Ingest documents into the knowledge base.
    
    Accepts URLs or file paths to index.
    """
    if not request.urls and not request.files:
        raise HTTPException(
            status_code=400,
            detail="Must provide at least one URL or file path"
        )
    
    try:
        from retriever import HybridRetriever
        
        retriever = HybridRetriever()
        chunks = retriever.ingest_documents(
            source_urls=request.urls if request.urls else None,
            source_files=request.files if request.files else None
        )
        
        return IngestResponse(
            success=True,
            chunks_indexed=chunks,
            message=f"Successfully indexed {chunks} chunks"
        )
        
    except Exception as e:
        return IngestResponse(
            success=False,
            chunks_indexed=0,
            message=f"Error: {str(e)}"
        )


@router.delete("/documents")
async def clear_documents(confirm: bool = False):
    """
    Clear all documents from the knowledge base.
    
    Requires confirm=true query parameter.
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Must pass confirm=true to delete all documents"
        )
    
    try:
        from retriever import HybridRetriever
        
        retriever = HybridRetriever()
        retriever.clear_collection()
        
        return {"success": True, "message": "Knowledge base cleared"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
