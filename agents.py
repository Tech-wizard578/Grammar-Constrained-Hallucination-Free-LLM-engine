"""Agentic nodes for LangGraph workflow.

This module defines the building blocks of the hallucination-free engine:
- Retrieve: Fetch relevant documents from vector DB
- Grade: Filter irrelevant documents (CRAG)
- Web Search: Fallback to web search if no relevant docs
- Generate: Create structured response with citations
- Verify: Check for hallucinations (Self-RAG)
"""

from openai import OpenAI
from schemas import HallucinationFreeResponse, DocumentRelevance, HallucinationCheck, Citation, VerificationQuestions, VerificationAnswer, ConsistencyCheck
from typing import TypedDict, List, Annotated, Optional
from langgraph.graph import add_messages
import instructor
import time
from config import DEFAULT_MODEL, SMART_MODEL, TAVILY_API_KEY, API_KEY, API_BASE_URL, USE_OPENROUTER, MAX_RETRIES
import os


# ============ INITIALIZE LLMs ============

# API timeout for all calls (seconds)
API_TIMEOUT = 30

# Create native OpenAI client (works with OpenRouter via base_url)
openai_kwargs = {"api_key": API_KEY, "timeout": API_TIMEOUT}
if API_BASE_URL:
    openai_kwargs["base_url"] = API_BASE_URL

# Create OpenAI client
openai_client = OpenAI(**openai_kwargs)

# Patch with Instructor for structured output
# client_fast: for quick operations (grading, verification)
# client_smart: for complex generation tasks
client_fast = instructor.from_openai(openai_client)
client_smart = instructor.from_openai(openai_client)


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
    # Use hybrid retrieval combining dense (vector) + sparse (BM25) search
    documents = retriever.hybrid_retrieve(question, k=5, alpha=0.6)
    
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
            grade: DocumentRelevance = client_fast.chat.completions.create(
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
        # Suppress warnings from langchain_tavily package
        import warnings
        warnings.filterwarnings("ignore", message="Field name.*shadows an attribute in parent")
        
        # Try new package first, fall back to deprecated one
        try:
            from langchain_tavily import TavilySearch
            web_tool = TavilySearch(max_results=3)
            using_new_api = True
        except ImportError:
            from langchain_community.tools.tavily_search import TavilySearchResults
            web_tool = TavilySearchResults(k=3, api_key=TAVILY_API_KEY)
            using_new_api = False
        
        print(f"🔎 Searching web for: '{question}'")
        results = web_tool.invoke(question)
        
        # Handle different response formats
        if isinstance(results, str):
            # New API may return string - parse it
            import json
            try:
                results = json.loads(results)
            except:
                results = [{"content": results, "url": "web", "title": "Web Result"}]
        
        # Ensure results is a list
        if isinstance(results, dict):
            results = [results]
        
        # Convert to document format
        web_docs = []
        for i, result in enumerate(results):
            # Handle both dict and other formats
            if isinstance(result, dict):
                content = result.get("content", "") or result.get("snippet", "") or str(result)
                url = result.get("url", "web")
                title = result.get("title", "Web Result")
            else:
                content = str(result)
                url = "web"
                title = "Web Result"
            
            web_docs.append({
                "source_id": 1000 + i,  # Offset to distinguish from KB docs
                "content": content,
                "metadata": {
                    "source": url, 
                    "type": "web_search",
                    "title": title
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
    
    # Retry loop with exponential backoff
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            # Use Instructor for structured output
            response: HallucinationFreeResponse = client_smart.chat.completions.create(
                model=SMART_MODEL,
                response_model=HallucinationFreeResponse,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_retries=2  # Instructor's internal retries
            )
            
            state["generation"] = response
            
            print(f"✅ Generated response:")
            print(f"  Answer: {response.answer[:100]}...")
            print(f"  Confidence: {response.confidence}")
            print(f"  Citations: {len(response.citations)}")
            return state
            
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s...
                print(f"  ⚠️ Attempt {attempt + 1}/{MAX_RETRIES} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"❌ Generation failed after {MAX_RETRIES} attempts: {e}")
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

Verify if the answer's claims can be REASONABLY DERIVED from the context. 
- Paraphrasing is ALLOWED - the answer doesn't need to use exact words from context
- Only mark as unsupported if a claim introduces NEW FACTS not present or implied in context
- Common knowledge that reasonably follows from context is acceptable"""
    
    try:
        verification: HallucinationCheck = client_fast.chat.completions.create(
            model=DEFAULT_MODEL,
            response_model=HallucinationCheck,
            messages=[
                {
                    "role": "system", 
                    "content": "You verify if answers are supported by context. Allow paraphrasing and reasonable inferences. Only flag TRUE hallucinations - claims that introduce completely new facts NOT derivable from the context. Do NOT flag paraphrased content as hallucinations."
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


# ============ NODE 6: CHAIN OF VERIFICATION (CoVe) ============

def chain_of_verification_node(state: GraphState) -> GraphState:
    """Apply Chain of Verification (CoVe) to refine the answer.
    
    CoVe Process:
    1. Generate verification questions about the answer
    2. Answer each question independently using the context
    3. Compare answers and refine if inconsistencies found
    """
    print("\n" + "="*60)
    print("🔗 CHAIN OF VERIFICATION NODE")
    print("="*60)
    
    generation = state.get("generation")
    if not generation:
        print("⚠️ No generation to verify with CoVe")
        return state
    
    documents = state["documents"]
    context = "\n\n".join([doc['content'] for doc in documents])
    
    try:
        # Step 1: Generate verification questions
        verification_prompt = f"""Given this answer: "{generation.answer}"
Generate exactly 3 short factual questions to verify the accuracy of this answer.
Each question should be answerable from the context."""

        questions_response = client_fast.chat.completions.create(
            model=DEFAULT_MODEL,
            response_model=VerificationQuestions,
            messages=[
                {"role": "system", "content": "You are a verification assistant. Generate short, focused verification questions. Return valid JSON only."},
                {"role": "user", "content": verification_prompt}
            ],
            max_retries=2
        )
        questions = questions_response.questions
        
        print(f"  📝 Generated {len(questions[:3])} verification questions")
        
        # Step 2: Answer each question with better error handling
        verified = []
        for i, q in enumerate(questions[:3]):
            try:
                ans_response = client_fast.chat.completions.create(
                    model=DEFAULT_MODEL,
                    response_model=VerificationAnswer,
                    messages=[
                        {"role": "system", "content": "You are a fact-checker. Answer the question in 1-2 sentences based ONLY on the provided context. If the context doesn't contain the answer, say 'Not found in context'. Return valid JSON."},
                        {"role": "user", "content": f"Context:\n{context[:1500]}\n\nQuestion: {q}\n\nProvide a brief factual answer."}
                    ],
                    max_retries=2
                )
                verified.append(f"Q: {q}\nA: {ans_response.answer}")
                print(f"    Q{i+1}: {q}")
            except Exception as q_error:
                print(f"    ⚠️ Skipping Q{i+1} due to error: {str(q_error)[:50]}")
                # Continue with other questions instead of failing entirely
                continue
        
        # Only proceed with consistency check if we have verified answers
        if verified:
            # Step 3: Check consistency
            consistency = client_fast.chat.completions.create(
                model=DEFAULT_MODEL,
                response_model=ConsistencyCheck,
                messages=[
                    {"role": "system", "content": "You are a consistency checker. Determine if the original answer aligns with the verification answers. Return valid JSON with is_consistent (boolean) and optionally refined_answer (string)."},
                    {"role": "user", "content": f"Original answer: {generation.answer}\n\nVerification Q&A:\n{chr(10).join(verified)}\n\nIs the original answer consistent with these verification answers?"}
                ],
                max_retries=2
            )
            
            if not consistency.is_consistent and consistency.refined_answer:
                print(f"  ⚠️ Refining answer via CoVe...")
                generation.metadata = generation.metadata or {}
                generation.metadata["original_answer"] = generation.answer
                generation.answer = consistency.refined_answer
                generation.metadata["cove_refined"] = True
            else:
                print(f"  ✅ Answer verified as consistent")
                generation.metadata = generation.metadata or {}
                generation.metadata["cove_verified"] = True
        else:
            print(f"  ⚠️ No verified answers - skipping consistency check")
            generation.metadata = generation.metadata or {}
            generation.metadata["cove_skipped"] = True
        
        state["generation"] = generation
        
    except Exception as e:
        print(f"  ⚠️ CoVe error (continuing with unverified answer): {str(e)[:100]}")
        # Don't fail - just skip CoVe and keep the original answer
        if generation:
            generation.metadata = generation.metadata or {}
            generation.metadata["cove_error"] = str(e)[:100]
            state["generation"] = generation
    
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
