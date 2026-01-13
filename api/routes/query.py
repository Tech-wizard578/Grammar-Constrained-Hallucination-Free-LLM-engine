"""Query route for Hallucination-Free Engine API."""

from fastapi import APIRouter, HTTPException
from api.models import QueryRequest, QueryResponse, CitationResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def run_query(request: QueryRequest):
    """
    Run a query through the hallucination-free engine.
    
    Returns structured response with answer, citations, and confidence.
    """
    try:
        # Import engine components
        from retriever import HybridRetriever
        from graph import build_hallucination_free_graph, run_query as engine_query
        
        # Initialize retriever and build graph
        retriever = HybridRetriever()
        app = build_hallucination_free_graph(retriever)
        
        # Execute query
        result = engine_query(app, request.question, verbose=request.verbose)
        
        # Format response
        response_data = {
            "success": result.get("success", False),
            "elapsed_time_seconds": result.get("elapsed_time_seconds", 0),
            "iterations": result.get("iterations", 0),
            "documents_retrieved": result.get("documents_retrieved", 0),
            "errors": result.get("errors", []),
            "citations": []
        }
        
        # Extract generation details if available
        generation = result.get("response")
        if generation:
            response_data["answer"] = generation.answer
            response_data["reasoning"] = generation.reasoning
            response_data["confidence"] = generation.confidence
            response_data["citations"] = [
                CitationResponse(
                    source_id=c.source_id,
                    quote=c.quote,
                    relevance_score=c.relevance_score
                )
                for c in generation.citations
            ]
        
        return QueryResponse(**response_data)
        
    except Exception as e:
        return QueryResponse(
            success=False,
            errors=[str(e)],
            elapsed_time_seconds=0
        )
