"""Pytest configuration and fixtures for hallucination-free engine tests."""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing without API calls."""
    with patch('openai.OpenAI') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def sample_documents():
    """Sample retrieved documents for testing."""
    return [
        {
            "source_id": 0,
            "content": "Python is a high-level programming language known for its simplicity.",
            "metadata": {"source": "test"},
            "relevance_score": 0.95
        },
        {
            "source_id": 1,
            "content": "Machine learning is a subset of artificial intelligence.",
            "metadata": {"source": "test"},
            "relevance_score": 0.85
        }
    ]


@pytest.fixture
def sample_graph_state(sample_documents):
    """Sample graph state for testing nodes."""
    return {
        "question": "What is Python?",
        "documents": sample_documents,
        "generation": None,
        "web_search_needed": False,
        "iteration_count": 0,
        "errors": []
    }


@pytest.fixture
def mock_retriever():
    """Mock HybridRetriever for testing."""
    mock = MagicMock()
    mock.collection.count.return_value = 10
    mock.hybrid_retrieve.return_value = [
        {
            "source_id": 0,
            "content": "Test document content",
            "metadata": {"source": "test"},
            "relevance_score": 0.9
        }
    ]
    return mock
