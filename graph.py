"""LangGraph workflow orchestration for hallucination-free engine.

This module wires together all agentic nodes into a self-correcting graph
that can detect and fix hallucinations through iterative refinement.
"""

from langgraph.graph import StateGraph, END
from agents import (
    GraphState, 
    retrieve_node, 
    grade_documents_node, 
    web_search_node,
    generate_node,
    verify_node,
    print_state_summary
)
from retriever import HybridRetriever
from functools import partial
from config import ITERATION_LIMIT


def build_hallucination_free_graph(retriever: HybridRetriever):
    """Construct the agentic workflow with conditional routing.
    
    Workflow:
    1. Retrieve documents from vector DB
    2. Grade documents for relevance (CRAG)
    3. [Conditional] Web search if no relevant docs
    4. Generate structured response with citations
    5. Verify for hallucinations (Self-RAG)
    6. [Conditional] Retry if hallucination detected (max 3 iterations)
    
    Args:
        retriever: HybridRetriever instance for document retrieval
        
    Returns:
        Compiled LangGraph application
    """
    print("🏗️ Building hallucination-free graph...")
    
    # Initialize graph with state schema
    workflow = StateGraph(GraphState)
    
    # Add nodes (bind retriever to retrieve_node using partial)
    workflow.add_node("retrieve", partial(retrieve_node, retriever=retriever))
    workflow.add_node("grade", grade_documents_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("verify", verify_node)
    
    # Set entry point
    workflow.set_entry_point("retrieve")
    
    # Define edges
    workflow.add_edge("retrieve", "grade")
    
    # Conditional: web search if no relevant docs found
    def should_web_search(state: GraphState) -> str:
        """Route to web search if all documents were filtered out."""
        if state.get("web_search_needed", False):
            print("🔀 Routing to web search (no relevant docs)")
            return "web_search"
        print("🔀 Routing to generation (relevant docs found)")
        return "generate"
    
    workflow.add_conditional_edges(
        "grade",
        should_web_search,
        {
            "web_search": "web_search",
            "generate": "generate"
        }
    )
    
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("generate", "verify")
    
    # Conditional: retry if hallucination detected (with iteration limit)
    def should_retry(state: GraphState) -> str:
        """Retry retrieval if hallucination detected and under iteration limit."""
        iteration = state.get("iteration_count", 0)
        has_generation = state.get("generation") is not None
        
        if not has_generation and iteration < ITERATION_LIMIT:
            print(f"🔀 Hallucination detected - retrying (iteration {iteration}/{ITERATION_LIMIT})")
            return "retrieve"
        
        if not has_generation and iteration >= ITERATION_LIMIT:
            print(f"⚠️ Max iterations reached ({ITERATION_LIMIT}) - ending with errors")
        else:
            print("🔀 Verification passed - ending workflow")
        
        return "end"
    
    workflow.add_conditional_edges(
        "verify",
        should_retry,
        {
            "retrieve": "retrieve",
            "end": END
        }
    )
    
    # Compile the graph
    app = workflow.compile()
    
    print("✅ Graph compiled successfully")
    
    return app


def run_query(app, question: str, verbose: bool = True) -> dict:
    """Run a query through the hallucination-free engine.
    
    Args:
        app: Compiled LangGraph application
        question: User's question
        verbose: Whether to print state summary
        
    Returns:
        Final state dictionary with generation
    """
    print("\n" + "="*80)
    print(f"🚀 RUNNING QUERY: {question}")
    print("="*80)
    
    # Initialize state
    initial_state = {
        "question": question,
        "documents": [],
        "generation": None,
        "web_search_needed": False,
        "iteration_count": 0,
        "errors": []
    }
    
    # Run the graph
    final_state = app.invoke(initial_state)
    
    if verbose:
        print_state_summary(final_state)
    
    return final_state


if __name__ == "__main__":
    """Test the complete graph with sample queries."""
    print("="*80)
    print("TESTING HALLUCINATION-FREE ENGINE")
    print("="*80)
    
    # Initialize retriever
    from retriever import HybridRetriever
    retriever = HybridRetriever()
    
    # Check if we have documents
    stats = retriever.get_stats()
    if stats["total_documents"] == 0:
        print("\n⚠️ No documents in knowledge base. Ingesting sample data...")
        retriever.ingest_documents(source_urls=[
            "https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
            "https://docs.python.org/3/tutorial/introduction.html"
        ])
    
    # Build graph
    app = build_hallucination_free_graph(retriever)
    
    # Test queries
    test_queries = [
        "What is retrieval-augmented generation?",
        "How do I use Python variables?",
        "What is the capital of France?"  # May trigger web search
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'='*80}")
        print(f"TEST {i}/{len(test_queries)}")
        print(f"{'='*80}")
        
        result = run_query(app, query)
        
        if result.get("generation"):
            gen = result["generation"]
            print("\n📝 FINAL RESPONSE:")
            print(f"  Answer: {gen.answer}")
            print(f"  Confidence: {gen.confidence}")
            print(f"  Citations ({len(gen.citations)}):")
            for cit in gen.citations:
                print(f"    [{cit.source_id}] \"{cit.quote[:60]}...\"")
        else:
            print("\n❌ No generation produced")
            print(f"  Errors: {result.get('errors', [])}")
    
    print("\n" + "="*80)
    print("✅ All graph tests completed!")
    print("="*80)
