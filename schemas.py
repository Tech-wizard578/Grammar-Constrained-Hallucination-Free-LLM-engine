"""Pydantic schemas for grammar-constrained structured outputs.

This module defines all output schemas that enforce EXACT structure for LLM responses.
The LLM is NOT allowed to return free text - every response must be a validated JSON object.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional
from datetime import datetime


# ============ CITATION SCHEMA (Evidence Tracking) ============

class Citation(BaseModel):
    """A single piece of evidence from the corpus.
    
    Ensures all claims are backed by verifiable sources with exact quotes.
    """
    source_id: int = Field(
        ..., 
        description="Index of the source document (0-indexed)",
        ge=0
    )
    quote: str = Field(
        ..., 
        description="Verbatim quote from source (max 200 chars)",
        min_length=10,
        max_length=200
    )
    relevance_score: float = Field(
        default=1.0,
        description="How relevant is this citation? (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    @field_validator('quote')
    @classmethod
    def quote_must_be_substantial(cls, v: str) -> str:
        """Ensure quote is meaningful and not just whitespace."""
        if len(v.strip()) < 10:
            raise ValueError('Quote too short to be meaningful')
        return v.strip()


# ============ MAIN RESPONSE SCHEMA ============

class HallucinationFreeResponse(BaseModel):
    """The ONLY allowed output format for the engine.
    
    Enforces structured reasoning with citations and confidence assessment.
    """
    
    reasoning: str = Field(
        ..., 
        description="Step-by-step derivation of answer from evidence. MUST reference source_ids.",
        min_length=50
    )
    
    answer: str = Field(
        ..., 
        description="Concise answer to user query (1-3 sentences)",
        min_length=20,
        max_length=500
    )
    
    citations: List[Citation] = Field(
        ..., 
        description="All evidence supporting the answer",
        min_length=1,
        max_length=10
    )
    
    confidence: Literal["High", "Medium", "Low"] = Field(
        ...,
        description="Self-assessed confidence based on evidence quality"
    )
    
    metadata: Optional[dict] = Field(
        default_factory=dict,
        description="Debug info: retrieval_time, model_used, etc."
    )

    @field_validator('reasoning')
    @classmethod
    def reasoning_must_cite_sources(cls, v: str, info) -> str:
        """Ensure reasoning actually references the citations.
        
        This prevents the LLM from providing reasoning that doesn't connect to sources.
        """
        # Check if reasoning mentions source_ids or documents
        v_lower = v.lower()
        if 'source' not in v_lower and 'document' not in v_lower and 'citation' not in v_lower:
            raise ValueError('Reasoning must explicitly reference sources (e.g., "Source 0 states...")')
        return v

    @field_validator('citations')
    @classmethod
    def citations_must_exist(cls, v: List[Citation]) -> List[Citation]:
        """Ensure at least one citation is provided."""
        if len(v) == 0:
            raise ValueError('At least one citation is required to support the answer')
        return v


# ============ DOCUMENT GRADER SCHEMA (for CRAG) ============

class DocumentRelevance(BaseModel):
    """Binary relevance score for CRAG filtering.
    
    Used to filter out irrelevant documents before generation.
    """
    binary_score: Literal["yes", "no"] = Field(
        description="Is document relevant to query?"
    )
    reasoning: str = Field(
        description="Why is this document relevant/irrelevant?",
        min_length=20
    )


# ============ HALLUCINATION DETECTOR SCHEMA (for Self-RAG) ============

class HallucinationCheck(BaseModel):
    """Validates if generated answer is supported by context.
    
    Used in the verification node to detect and correct hallucinations.
    """
    is_supported: bool = Field(
        description="Is EVERY claim in the answer backed by context?"
    )
    unsupported_claims: List[str] = Field(
        default_factory=list,
        description="List of claims that lack evidence"
    )
    fix_suggestion: Optional[str] = Field(
        default=None,
        description="How to fix hallucinations?"
    )

    @field_validator('unsupported_claims')
    @classmethod
    def unsupported_claims_required_if_not_supported(cls, v: List[str], info) -> List[str]:
        """If answer is not supported, must provide specific unsupported claims."""
        # Access is_supported from the model's data
        if hasattr(info, 'data') and not info.data.get('is_supported', True):
            if len(v) == 0:
                raise ValueError('Must specify which claims are unsupported when is_supported=False')
        return v


# ============ CHAIN OF VERIFICATION (CoVe) SCHEMAS ============

class VerificationQuestions(BaseModel):
    """List of questions to verify an answer's accuracy."""
    questions: List[str] = Field(
        ...,
        description="List of factual questions to verify the answer",
        min_length=1,
        max_length=5
    )


class VerificationAnswer(BaseModel):
    """Answer to a verification question based on context."""
    answer: str = Field(
        ...,
        description="Answer based on the provided context",
        min_length=5
    )


class ConsistencyCheck(BaseModel):
    """Result of checking answer consistency with verification."""
    is_consistent: bool = Field(
        ...,
        description="Is the original answer consistent with verification answers?"
    )
    refined_answer: Optional[str] = Field(
        default=None,
        description="Refined answer if inconsistencies were found"
    )


# ============ HELPER FUNCTIONS ============

def validate_response_schema(response_dict: dict) -> HallucinationFreeResponse:
    """Validate a dictionary against the HallucinationFreeResponse schema.
    
    Args:
        response_dict: Dictionary to validate
        
    Returns:
        Validated HallucinationFreeResponse object
        
    Raises:
        ValidationError: If the dictionary doesn't match the schema
    """
    return HallucinationFreeResponse(**response_dict)


if __name__ == "__main__":
    # Test valid response
    print("Testing valid response...")
    try:
        valid = HallucinationFreeResponse(
            reasoning="Based on source 0 which states 'Python is a high-level programming language', we can conclude that Python is indeed a programming language.",
            answer="Python is a high-level, interpreted programming language known for its simplicity and readability.",
            citations=[
                Citation(
                    source_id=0, 
                    quote="Python is a high-level programming language",
                    relevance_score=0.95
                )
            ],
            confidence="High"
        )
        print("✅ Valid response created successfully")
        print(valid.model_dump_json(indent=2))
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test invalid responses
    print("\n\nTesting invalid responses (should raise ValidationError)...")
    
    # Test 1: Reasoning too short
    print("\n1. Testing short reasoning...")
    try:
        invalid = HallucinationFreeResponse(
            reasoning="Short",  # Too short!
            answer="Python is a programming language.",
            citations=[Citation(source_id=0, quote="Python is great")],
            confidence="High"
        )
        print("❌ Should have raised ValidationError for short reasoning")
    except Exception as e:
        print(f"✅ Validation caught error: {type(e).__name__}")

    # Test 2: Empty citations
    print("\n2. Testing empty citations...")
    try:
        invalid = HallucinationFreeResponse(
            reasoning="Based on source 0, Python is a programming language used for various applications.",
            answer="Python is a programming language.",
            citations=[],  # Empty citations!
            confidence="High"
        )
        print("❌ Should have raised ValidationError for empty citations")
    except Exception as e:
        print(f"✅ Validation caught error: {type(e).__name__}")

    # Test 3: Invalid confidence literal
    print("\n3. Testing invalid confidence...")
    try:
        invalid = HallucinationFreeResponse(
            reasoning="Based on source 0, Python is a programming language.",
            answer="Python is a programming language.",
            citations=[Citation(source_id=0, quote="Python is a language")],
            confidence="Maybe"  # Invalid literal!
        )
        print("❌ Should have raised ValidationError for invalid confidence")
    except Exception as e:
        print(f"✅ Validation caught error: {type(e).__name__}")

    # Test 4: Reasoning without source references
    print("\n4. Testing reasoning without source references...")
    try:
        invalid = HallucinationFreeResponse(
            reasoning="Python is a great programming language that many people use for data science.",
            answer="Python is a programming language.",
            citations=[Citation(source_id=0, quote="Python is a language")],
            confidence="High"
        )
        print("❌ Should have raised ValidationError for reasoning without sources")
    except Exception as e:
        print(f"✅ Validation caught error: {type(e).__name__}")

    print("\n\n✅ All schema validation tests completed!")
