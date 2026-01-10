"""Agentic nodes for LangGraph workflow.

This module defines the building blocks of the hallucination-free engine:
- Retrieve: Fetch relevant documents from vector DB
- Grade: Filter irrelevant documents (CRAG)
- Web Search: Fallback to web search if no relevant docs
- Generate: Create structured response with citations
- Verify: Check for hallucinations (Self-RAG)
"""

from openai import OpenAI
from schemas import HallucinationFreeResponse, DocumentRelevance, HallucinationCheck, Citation
from typing import TypedDict, List, Annotated, Optional
from langgraph.graph import add_messages
import instructor
from config import DEFAULT_MODEL, SMART_MODEL, TAVILY_API_KEY, API_KEY, API_BASE_URL, USE_OPENROUTER
import os


# ============ INITIALIZE LLMs ============

# Create native OpenAI client (works with OpenRouter via base_url)
openai_kwargs = {"api_key": API_KEY}
if API_BASE_URL:
    openai_kwargs["base_url"] = API_BASE_URL

# Create OpenAI client
openai_client = OpenAI(**openai_kwargs)

# Patch with Instructor for structured output
client = instructor.from_openai(openai_client)
client_smart = client  # Use same client, different model at call time


# ============ GRAPH STATE ============

class GraphState(TypedDict):
    """The memory/state passed between nodes in the LangGraph workflow.
    
    This state persists across all nodes and tracks the entire execution.
    """
    question: str
    documents: List[dict]
    generation: Optional[HallucinationFreeResponse]
    web_search_needed: bool
    iteration_count: int
    errors: List[str]


# ============ NODE 1: RETRIEVE ============

def retrieve_node(state: GraphState, retriever) -> GraphState:
    """Fetch relevant documents from vector database.
    
    Args:
        state: Current graph state
        retriever: HybridRetriever instance
        
    Returns:
        Updated state with retrieved documents
    """
    print("\n" + "="*60)
    print("📚 RETRIEVE NODE")
    print("="*60)
    
    question = state["question"]
    documents = retriever.retrieve(question, k=5)
    
    state["documents"] = documents
    state["iteration_count"] = state.get("iteration_count", 0) + 1
    
    print(f"✅ Retrieved {len(documents)} documents (iteration {state['iteration_count']})")
    
    return state


# ============ NODE 2: GRADE DOCUMENTS (CRAG) ============

def grade_documents_node(state: GraphState) -> GraphState:
    """Filter out irrelevant documents using CRAG technique.
    
    Uses structured output to get binary relevance scores for each document.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with filtered documents
    """
    print("\n" + "="*60)
    print("🔍 GRADE DOCUMENTS NODE")
    print("="*60)
    
    question = state["question"]
    documents = state["documents"]
    
    if not documents:
        print("⚠️ No documents to grade")
        state["web_search_needed"] = True
        return state
    
    filtered_docs = []
    
    for doc in documents:
        # Use structured output to get binary relevance
        try:
            grade: DocumentRelevance = client.chat.completions.create(
                model=DEFAULT_MODEL,
                response_model=DocumentRelevance,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a document relevance grader. Determine if a document is relevant to answering the user's question."
                    },
                    {
                        "role": "user", 
                        "content": f"Question: {question}\n\nDocument: {doc['content'][:500]}\n\nIs this document relevant to answering the question?"
                    }
                ],
                max_retries=2
            )
            
            if grade.binary_score == "yes":
                filtered_docs.append(doc)
                print(f"  ✅ Kept doc {doc['source_id']}: {grade.reasoning[:60]}...")
            else:
                print(f"  ❌ Filtered doc {doc['source_id']}: {grade.reasoning[:60]}...")
                
        except Exception as e:
            print(f"  ⚠️ Error grading doc {doc['source_id']}: {e}")
            # Keep document if grading fails (conservative approach)
            filtered_docs.append(doc)
    
    state["documents"] = filtered_docs
    state["web_search_needed"] = len(filtered_docs) == 0
    
    print(f"\n📊 Grading complete: {len(filtered_docs)}/{len(documents)} documents kept")
    if state["web_search_needed"]:
        print("⚠️ No relevant documents found - will trigger web search")
    
    return state


# ============ NODE 3: WEB SEARCH (Fallback) ============

def web_search_node(state: GraphState) -> GraphState:
    """Fallback to web search if no relevant docs found in knowledge base.
    
    Uses Tavily API for web search.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with web search results
    """
    print("\n" + "="*60)
    print("🌐 WEB SEARCH NODE")
    print("="*60)
    
    question = state["question"]
    
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults
        
        web_tool = TavilySearchResults(k=3, api_key=TAVILY_API_KEY)
        
        print(f"🔎 Searching web for: '{question}'")
        results = web_tool.invoke({"query": question})
        
        # Convert to document format
        web_docs = []
        for i, result in enumerate(results):
            web_docs.append({
                "source_id": 1000 + i,  # Offset to distinguish from KB docs
                "content": result.get("content", ""),
                "metadata": {
                    "source": result.get("url", "web"), 
                    "type": "web_search",
                    "title": result.get("title", "")
                },
                "relevance_score": 0.8  # Assume web results are relevant
            })
        
        state["documents"] = web_docs
        state["web_search_needed"] = False
        
        print(f"✅ Found {len(web_docs)} web results")
        for doc in web_docs:
            print(f"  - {doc['metadata'].get('title', 'Untitled')}: {doc['content'][:60]}...")
        
    except Exception as e:
        print(f"❌ Web search failed: {e}")
        state["errors"] = state.get("errors", []) + [f"Web search error: {e}"]
        # Continue with empty documents - generation will handle this
    
    return state


# ============ NODE 4: GENERATE ============

def generate_node(state: GraphState) -> GraphState:
    """Generate structured response with citations using Instructor.
    
    Enforces HallucinationFreeResponse schema at the API level.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with generated response
    """
    print("\n" + "="*60)
    print("✍️ GENERATE NODE")
    print("="*60)
    
    question = state["question"]
    documents = state["documents"]
    
    if not documents:
        print("⚠️ No documents available for generation")
        # Create a low-confidence response
        state["generation"] = HallucinationFreeResponse(
            reasoning="No relevant documents were found in the knowledge base or web search to answer this question.",
            answer="I cannot provide a reliable answer as no relevant information was found.",
            citations=[Citation(source_id=0, quote="No sources available", relevance_score=0.0)],
            confidence="Low",
            metadata={"error": "no_documents"}
        )
        return state
    
    # Build context string with source IDs
    context = "\n\n".join([
        f"[Source {doc['source_id']}]: {doc['content']}"
        for doc in documents
    ])
    
    system_prompt = """You are a precise AI that ONLY answers from provided context.

CRITICAL RULES:
1. EVERY claim must have a citation with source_id
2. Use ONLY information from the [Source N] documents provided
3. If context is insufficient, set confidence to Low
4. Quote exact phrases for citations (verbatim, max 200 chars)
5. Reasoning must show work: "Source 2 states X, therefore Y"
6. Never make up information not in the sources

Your output MUST match the HallucinationFreeResponse schema with:
- reasoning: Step-by-step derivation citing sources
- answer: Concise answer (1-3 sentences)
- citations: List of Citation objects with exact quotes
- confidence: High/Medium/Low based on evidence quality"""
    
    user_prompt = f"""Context:
{context}

Question: {question}

Provide a structured response with reasoning, answer, and citations."""
    
    try:
        # Use Instructor for structured output
        response: HallucinationFreeResponse = client_smart.chat.completions.create(
            model=SMART_MODEL,
            response_model=HallucinationFreeResponse,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_retries=3
        )
        
        state["generation"] = response
        
        print(f"✅ Generated response:")
        print(f"  Answer: {response.answer[:100]}...")
        print(f"  Confidence: {response.confidence}")
        print(f"  Citations: {len(response.citations)}")
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        state["errors"] = state.get("errors", []) + [f"Generation error: {e}"]
        state["generation"] = None
    
    return state


# ============ NODE 5: VERIFY (Self-RAG) ============

def verify_node(state: GraphState) -> GraphState:
    """Check if generated answer is supported by documents (Self-RAG).
    
    Uses structured output to detect hallucinations.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state (generation set to None if hallucination detected)
    """
    print("\n" + "="*60)
    print("🔬 VERIFY NODE")
    print("="*60)
    
    generation = state.get("generation")
    
    if not generation:
        print("⚠️ No generation to verify")
        return state
    
    documents = state["documents"]
    
    if not documents:
        print("⚠️ No documents to verify against")
        return state
    
    # Build context from documents
    context = "\n\n".join([doc['content'] for doc in documents])
    
    verification_prompt = f"""Context:
{context[:2000]}

Answer to verify:
{generation.answer}

Reasoning provided:
{generation.reasoning}

Verify if EVERY claim in the answer is supported by the context. Be STRICT - if any claim lacks evidence, mark as unsupported."""
    
    try:
        verification: HallucinationCheck = client.chat.completions.create(
            model=DEFAULT_MODEL,
            response_model=HallucinationCheck,
            messages=[
                {
                    "role": "system", 
                    "content": "You verify if answers are fully supported by context. Be STRICT - any unsupported claim means is_supported=False."
                },
                {"role": "user", "content": verification_prompt}
            ],
            max_retries=2
        )
        
        if not verification.is_supported:
            print(f"  ⚠️ HALLUCINATION DETECTED!")
            print(f"  Unsupported claims: {verification.unsupported_claims}")
            if verification.fix_suggestion:
                print(f"  Fix suggestion: {verification.fix_suggestion}")
            
            state["errors"] = state.get("errors", []) + verification.unsupported_claims
            state["generation"] = None  # Force regeneration
        else:
            print(f"  ✅ Answer verified as factual")
            
    except Exception as e:
        print(f"  ⚠️ Verification error: {e}")
        # If verification fails, keep the generation (conservative)
    
    return state


# ============ HELPER FUNCTIONS ============

def print_state_summary(state: GraphState):
    """Print a summary of the current state for debugging."""
    print("\n" + "="*60)
    print("📊 STATE SUMMARY")
    print("="*60)
    print(f"Question: {state.get('question', 'N/A')}")
    print(f"Documents: {len(state.get('documents', []))}")
    print(f"Generation: {'✅' if state.get('generation') else '❌'}")
    print(f"Web search needed: {state.get('web_search_needed', False)}")
    print(f"Iteration: {state.get('iteration_count', 0)}")
    print(f"Errors: {len(state.get('errors', []))}")
    print("="*60)


if __name__ == "__main__":
    """Test individual nodes."""
    print("Testing individual nodes requires a retriever instance.")
    print("Run the full graph test in graph.py instead.")
