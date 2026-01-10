"""Retrieval layer for RAG pipeline using ChromaDB.

This module handles document ingestion, chunking, embedding, and retrieval.
Supports both web URLs and PDF files as input sources.
"""

import chromadb
from chromadb.utils import embedding_functions
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Optional
import os
from config import (
    API_KEY,
    OPENAI_API_KEY,
    CHROMA_DB_PATH, 
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K_RETRIEVAL,
    EMBEDDING_MODEL,
    USE_OPENROUTER
)


class HybridRetriever:
    """Combines dense (vector) and sparse (BM25) retrieval for optimal results.
    
    Uses ChromaDB for persistent vector storage with configurable embedding models.
    """
    
    def __init__(self, collection_name: str = None):
        """Initialize the retriever with ChromaDB and embedding function.
        
        Args:
            collection_name: Name of the ChromaDB collection (defaults to config)
        """
        self.collection_name = collection_name or COLLECTION_NAME
        
        # Initialize ChromaDB with persistence
        print(f"📦 Initializing ChromaDB at {CHROMA_DB_PATH}...")
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        
        # Choose embedding function based on API provider
        # Note: OpenRouter doesn't support embeddings API, so use local embeddings or OpenAI directly
        if OPENAI_API_KEY and not USE_OPENROUTER:
            print(f"🔑 Using OpenAI embeddings: {EMBEDDING_MODEL}")
            self.embed_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=OPENAI_API_KEY,
                model_name=EMBEDDING_MODEL
            )
        else:
            # Fallback to local embeddings (required when using OpenRouter)
            print("🏠 Using local Sentence Transformer embeddings (all-MiniLM-L6-v2)")
            if USE_OPENROUTER:
                print("   Note: OpenRouter doesn't support embeddings API")
            self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embed_fn,
            metadata={"description": "Hallucination-free knowledge base"}
        )
        
        # Initialize text splitter with tiktoken for accurate token counting
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            model_name="gpt-4"  # Use GPT-4 tokenizer for consistency
        )
        
        # BM25 index for sparse retrieval (initialized on first use)
        self.bm25_index = None
        self.bm25_corpus = []
        self.bm25_docs = []
        
        print(f"✅ Retriever initialized with {self.collection.count()} existing documents")
    
    def ingest_documents(
        self, 
        source_urls: Optional[List[str]] = None, 
        source_files: Optional[List[str]] = None
    ) -> int:
        """Load, chunk, and index documents into the vector database.
        
        Args:
            source_urls: List of web URLs to scrape and index
            source_files: List of file paths (PDFs, text files) to index
            
        Returns:
            Number of chunks indexed
            
        Raises:
            ValueError: If neither source_urls nor source_files provided
        """
        if not source_urls and not source_files:
            raise ValueError("Must provide either source_urls or source_files")
        
        documents = []
        
        # Load from URLs
        if source_urls:
            print(f"🌐 Loading {len(source_urls)} web pages...")
            try:
                loader = WebBaseLoader(source_urls)
                web_docs = loader.load()
                documents.extend(web_docs)
                print(f"  ✅ Loaded {len(web_docs)} web documents")
            except Exception as e:
                print(f"  ⚠️ Error loading web pages: {e}")
        
        # Load from files (PDFs, etc.)
        if source_files:
            print(f"📄 Loading {len(source_files)} files...")
            for file_path in source_files:
                try:
                    # Determine loader based on file extension
                    if file_path.endswith('.pdf'):
                        from langchain_community.document_loaders import PyPDFLoader
                        loader = PyPDFLoader(file_path)
                    else:
                        from langchain_community.document_loaders import TextLoader
                        loader = TextLoader(file_path)
                    
                    file_docs = loader.load()
                    documents.extend(file_docs)
                    print(f"  ✅ Loaded {file_path}")
                except Exception as e:
                    print(f"  ⚠️ Error loading {file_path}: {e}")
        
        if not documents:
            print("❌ No documents loaded successfully")
            return 0
        
        # Chunk documents
        print(f"✂️ Chunking {len(documents)} documents (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"  ✅ Created {len(chunks)} chunks")
        
        # Get current count to offset IDs
        current_count = self.collection.count()
        
        # Index into ChromaDB
        print(f"💾 Indexing {len(chunks)} chunks into ChromaDB...")
        self.collection.add(
            documents=[chunk.page_content for chunk in chunks],
            metadatas=[{
                "source": chunk.metadata.get("source", "unknown"),
                "chunk_id": i,
                "total_chunks": len(chunks)
            } for i, chunk in enumerate(chunks)],
            ids=[f"doc_{current_count + i}" for i in range(len(chunks))]
        )
        
        print(f"✅ Successfully indexed {len(chunks)} chunks (total: {self.collection.count()})")
        return len(chunks)
    
    def retrieve(self, query: str, k: int = None) -> List[Dict]:
        """Retrieve top-k most relevant chunks for a query.
        
        Args:
            query: User's question or search query
            k: Number of results to return (defaults to config TOP_K_RETRIEVAL)
            
        Returns:
            List of dictionaries with keys: source_id, content, metadata, relevance_score
        """
        k = k or TOP_K_RETRIEVAL
        
        if self.collection.count() == 0:
            print("⚠️ Warning: No documents in collection. Please ingest documents first.")
            return []
        
        print(f"🔍 Retrieving top {k} documents for query: '{query[:50]}...'")
        
        # Query ChromaDB
        results = self.collection.query(
            query_texts=[query],
            n_results=min(k, self.collection.count())  # Don't request more than available
        )
        
        # Format results
        retrieved_docs = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            retrieved_docs.append({
                "source_id": i,
                "content": doc,
                "metadata": metadata,
                "relevance_score": 1 - distance  # Convert distance to similarity (0-1)
            })
        
        print(f"  ✅ Retrieved {len(retrieved_docs)} documents")
        for i, doc in enumerate(retrieved_docs[:3]):  # Show top 3
            print(f"    [{i}] Score: {doc['relevance_score']:.3f} | {doc['content'][:60]}...")
        
        return retrieved_docs
    
    def _build_bm25_index(self):
        """Build BM25 index from all documents in collection."""
        try:
            from rank_bm25 import BM25Okapi
            
            # Get all documents from ChromaDB
            all_docs = self.collection.get()
            if not all_docs['documents']:
                return
            
            self.bm25_docs = all_docs['documents']
            # Tokenize documents for BM25
            self.bm25_corpus = [doc.lower().split() for doc in self.bm25_docs]
            self.bm25_index = BM25Okapi(self.bm25_corpus)
            print(f"  📊 Built BM25 index with {len(self.bm25_corpus)} documents")
        except ImportError:
            print("  ⚠️ rank-bm25 not installed, skipping BM25 index")
    
    def hybrid_retrieve(self, query: str, k: int = None, alpha: float = 0.5) -> List[Dict]:
        """Hybrid retrieval combining dense (vector) and sparse (BM25) search.
        
        Args:
            query: User's question or search query
            k: Number of results to return
            alpha: Weight for dense vs sparse (0=sparse only, 1=dense only, 0.5=balanced)
            
        Returns:
            List of documents with combined relevance scores
        """
        k = k or TOP_K_RETRIEVAL
        
        if self.collection.count() == 0:
            return []
        
        print(f"🔍 Hybrid retrieval for: '{query[:50]}...'")
        
        # Build BM25 index if not exists
        if self.bm25_index is None:
            self._build_bm25_index()
        
        # Dense retrieval (vector search)
        dense_results = self.collection.query(
            query_texts=[query],
            n_results=min(k * 2, self.collection.count())
        )
        
        # Create score dictionary for dense results
        doc_scores = {}
        for i, (doc, distance) in enumerate(zip(
            dense_results['documents'][0],
            dense_results['distances'][0]
        )):
            dense_score = 1 - distance
            doc_scores[doc] = {"dense": dense_score, "sparse": 0.0}
        
        # BM25 sparse retrieval
        if self.bm25_index:
            tokenized_query = query.lower().split()
            bm25_scores = self.bm25_index.get_scores(tokenized_query)
            
            # Normalize BM25 scores
            max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
            for i, doc in enumerate(self.bm25_docs):
                sparse_score = bm25_scores[i] / max_bm25
                if doc in doc_scores:
                    doc_scores[doc]["sparse"] = sparse_score
                elif sparse_score > 0.1:  # Only add if significant
                    doc_scores[doc] = {"dense": 0.0, "sparse": sparse_score}
        
        # Combine scores using weighted average
        combined_results = []
        for doc, scores in doc_scores.items():
            combined_score = alpha * scores["dense"] + (1 - alpha) * scores["sparse"]
            combined_results.append({
                "source_id": len(combined_results),
                "content": doc,
                "metadata": {"retrieval_type": "hybrid"},
                "relevance_score": combined_score,
                "dense_score": scores["dense"],
                "sparse_score": scores["sparse"]
            })
        
        # Sort by combined score and return top k
        combined_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        results = combined_results[:k]
        
        print(f"  ✅ Hybrid retrieval: {len(results)} documents")
        for i, doc in enumerate(results[:3]):
            print(f"    [{i}] Combined: {doc['relevance_score']:.3f} (D:{doc['dense_score']:.2f}, S:{doc['sparse_score']:.2f})")
        
        return results
    
    def clear_collection(self):
        """Delete all documents from the collection."""
        print(f"🗑️ Clearing collection '{self.collection_name}'...")
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embed_fn
        )
        print("✅ Collection cleared")
    
    def get_stats(self) -> Dict:
        """Get statistics about the current collection."""
        return {
            "collection_name": self.collection_name,
            "total_documents": self.collection.count(),
            "embedding_model": EMBEDDING_MODEL if OPENAI_API_KEY else "all-MiniLM-L6-v2",
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP
        }


if __name__ == "__main__":
    """Test the retriever with sample data."""
    print("=" * 60)
    print("TESTING HYBRID RETRIEVER")
    print("=" * 60)
    
    # Initialize retriever
    retriever = HybridRetriever()
    
    # Show current stats
    stats = retriever.get_stats()
    print(f"\n📊 Current Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test ingestion with sample URLs
    print("\n" + "=" * 60)
    print("TEST 1: Ingesting Sample Documents")
    print("=" * 60)
    
    sample_urls = [
        "https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
        "https://docs.python.org/3/tutorial/introduction.html"
    ]
    
    try:
        num_chunks = retriever.ingest_documents(source_urls=sample_urls)
        print(f"\n✅ Ingestion test passed: {num_chunks} chunks indexed")
    except Exception as e:
        print(f"\n❌ Ingestion test failed: {e}")
    
    # Test retrieval
    print("\n" + "=" * 60)
    print("TEST 2: Retrieving Documents")
    print("=" * 60)
    
    test_queries = [
        "What is retrieval-augmented generation?",
        "How do I use Python variables?",
        "What is machine learning?"  # Should have low relevance
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = retriever.retrieve(query, k=3)
        
        if results:
            print(f"  Top result: {results[0]['content'][:100]}...")
            print(f"  Relevance: {results[0]['relevance_score']:.3f}")
        else:
            print("  No results found")
    
    print("\n" + "=" * 60)
    print("✅ All retriever tests completed!")
    print("=" * 60)
