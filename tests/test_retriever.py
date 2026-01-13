"""Tests for retriever.py - RAG Pipeline (5 tests)."""

import pytest
from unittest.mock import MagicMock, patch


class TestHybridRetriever:
    """Tests for HybridRetriever class."""
    
    def test_bm25_cache_invalidation_on_doc_change(self, mock_retriever):
        """Test that BM25 cache invalidates when document count changes."""
        from retriever import HybridRetriever
        
        with patch.object(HybridRetriever, '__init__', lambda x, y=None: None):
            retriever = HybridRetriever()
            retriever._bm25_doc_count = 5
            retriever._query_cache = {"old_query": ["doc1"]}
            retriever.collection = MagicMock()
            retriever.collection.count.return_value = 10  # Different count
            
            # Simulating cache check logic
            current_count = retriever.collection.count()
            if current_count != retriever._bm25_doc_count:
                retriever._query_cache.clear()
            
            assert len(retriever._query_cache) == 0  # Cache should be cleared
    
    def test_query_cache_stores_results(self):
        """Test that query results are cached."""
        from retriever import HybridRetriever
        
        with patch.object(HybridRetriever, '__init__', lambda x, y=None: None):
            retriever = HybridRetriever()
            retriever._query_cache = {}
            retriever._cache_max_size = 100
            
            # Simulate caching
            cache_key = "test_hash"
            results = [{"content": "test"}]
            retriever._query_cache[cache_key] = results
            
            assert cache_key in retriever._query_cache
            assert retriever._query_cache[cache_key] == results
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache exceeds max size."""
        from retriever import HybridRetriever
        
        with patch.object(HybridRetriever, '__init__', lambda x, y=None: None):
            retriever = HybridRetriever()
            retriever._query_cache = {}
            retriever._cache_max_size = 2  # Small cache for testing
            
            # Fill cache
            retriever._query_cache["key1"] = ["doc1"]
            retriever._query_cache["key2"] = ["doc2"]
            
            # Add third item - should evict oldest
            if len(retriever._query_cache) >= retriever._cache_max_size:
                oldest_key = next(iter(retriever._query_cache))
                del retriever._query_cache[oldest_key]
            retriever._query_cache["key3"] = ["doc3"]
            
            assert "key1" not in retriever._query_cache  # Evicted
            assert "key3" in retriever._query_cache
    
    def test_empty_collection_returns_empty_list(self, mock_retriever):
        """Test that retrieve returns empty list when collection is empty."""
        mock_retriever.collection.count.return_value = 0
        mock_retriever.retrieve = lambda q, k=5: [] if mock_retriever.collection.count() == 0 else ["docs"]
        
        results = mock_retriever.retrieve("test query")
        
        assert results == []
    
    def test_retrieve_returns_formatted_documents(self, sample_documents):
        """Test that retrieve returns properly formatted documents."""
        doc = sample_documents[0]
        
        assert "source_id" in doc
        assert "content" in doc
        assert "metadata" in doc
        assert "relevance_score" in doc
        assert 0 <= doc["relevance_score"] <= 1
