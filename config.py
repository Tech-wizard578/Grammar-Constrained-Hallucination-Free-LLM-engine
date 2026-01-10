"""Configuration management for the Hallucination-Free LLM Engine."""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Model Configuration
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
SMART_MODEL = os.getenv("SMART_MODEL", "gpt-4o")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# ChromaDB Configuration
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "hallucination_free_kb")

# Retrieval Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "5"))

# Evaluation Configuration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
ITERATION_LIMIT = int(os.getenv("ITERATION_LIMIT", "3"))

# Validation
def validate_config():
    """Validate that required configuration is present."""
    errors = []
    
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required")
    
    if not TAVILY_API_KEY:
        errors.append("TAVILY_API_KEY is required (for web search fallback)")
    
    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True

def get_config_summary():
    """Get a summary of current configuration."""
    return {
        "default_model": DEFAULT_MODEL,
        "smart_model": SMART_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "chroma_db_path": CHROMA_DB_PATH,
        "collection_name": COLLECTION_NAME,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "top_k_retrieval": TOP_K_RETRIEVAL,
        "max_retries": MAX_RETRIES,
        "iteration_limit": ITERATION_LIMIT,
    }
