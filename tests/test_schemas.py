"""Tests for schemas.py - Pydantic Models (6 tests)."""

import pytest
from pydantic import ValidationError


class TestCitation:
    """Tests for Citation schema."""
    
    def test_valid_citation_creation(self):
        """Test creating a valid citation."""
        from schemas import Citation
        
        citation = Citation(
            source_id=0,
            quote="Python is a programming language",
            relevance_score=0.95
        )
        
        assert citation.source_id == 0
        assert citation.relevance_score == 0.95
    
    def test_citation_quote_too_short_raises_error(self):
        """Test that quote < 10 chars raises validation error."""
        from schemas import Citation
        
        with pytest.raises(ValidationError):
            Citation(source_id=0, quote="Short")


class TestHallucinationFreeResponse:
    """Tests for main response schema."""
    
    def test_valid_response_creation(self):
        """Test creating a valid HallucinationFreeResponse."""
        from schemas import HallucinationFreeResponse, Citation
        
        response = HallucinationFreeResponse(
            reasoning="Based on source 0, Python is a high-level programming language.",
            answer="Python is a high-level, interpreted programming language.",
            citations=[Citation(source_id=0, quote="Python is a programming language")],
            confidence="High"
        )
        
        assert response.confidence == "High"
        assert len(response.citations) == 1
    
    def test_reasoning_without_source_reference_raises_error(self):
        """Test that reasoning must reference sources."""
        from schemas import HallucinationFreeResponse, Citation
        
        with pytest.raises(ValidationError, match="reference sources"):
            HallucinationFreeResponse(
                reasoning="Python is great for data science and web development.",
                answer="Python is a programming language.",
                citations=[Citation(source_id=0, quote="Python is a language")],
                confidence="High"
            )
    
    def test_empty_citations_raises_error(self):
        """Test that at least one citation is required."""
        from schemas import HallucinationFreeResponse
        
        with pytest.raises(ValidationError):
            HallucinationFreeResponse(
                reasoning="Based on source 0, Python is great.",
                answer="Python is a programming language.",
                citations=[],
                confidence="High"
            )
    
    def test_extra_fields_forbidden(self):
        """Test that extra fields raise validation error (ConfigDict extra='forbid')."""
        from schemas import HallucinationFreeResponse, Citation
        
        with pytest.raises(ValidationError):
            HallucinationFreeResponse(
                reasoning="Based on source 0, Python is a language.",
                answer="Python is a programming language.",
                citations=[Citation(source_id=0, quote="Python is a language")],
                confidence="High",
                extra_field="should_fail"  # Not allowed
            )


class TestDocumentRelevance:
    """Tests for CRAG grading schema."""
    
    def test_valid_relevance_score(self):
        """Test creating valid document relevance."""
        from schemas import DocumentRelevance
        
        relevance = DocumentRelevance(
            binary_score="yes",
            reasoning="This document directly answers the question about Python."
        )
        
        assert relevance.binary_score == "yes"
