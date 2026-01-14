"""Configuration management for the Hallucination-Free LLM Engine."""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# ============ ENVIRONMENT PROFILES ============
# Supports: development, production, test
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Environment-specific settings
if ENVIRONMENT == "production":
    # Stricter settings for production
    LOG_LEVEL = "WARNING"
    ENABLE_DEBUG_OUTPUT = False
elif ENVIRONMENT == "test":
    LOG_LEVEL = "DEBUG"
    ENABLE_DEBUG_OUTPUT = True
else:  # development
    LOG_LEVEL = "INFO"
    ENABLE_DEBUG_OUTPUT = True

# API Keys - Support OpenAI, OpenRouter, and Groq
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Determine which API to use (priority: Groq > OpenRouter > OpenAI)
USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"
USE_OPENROUTER = os.getenv("USE_OPENROUTER", "false").lower() == "true"

# Validate mutual exclusivity of providers
if sum([USE_GROQ, USE_OPENROUTER]) > 1:
    raise ValueError("Only one API provider can be active at a time (USE_GROQ or USE_OPENROUTER, not both)")

if USE_GROQ:
    API_KEY = GROQ_API_KEY
    API_BASE_URL = "https://api.groq.com/openai/v1"
elif USE_OPENROUTER:
    API_KEY = OPENROUTER_API_KEY
    API_BASE_URL = "https://openrouter.ai/api/v1"
else:
    API_KEY = OPENAI_API_KEY
    API_BASE_URL = None

# Model Configuration
# For Groq: "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"
# For OpenRouter: use format "provider/model" 
# For OpenAI: "gpt-4o-mini", "gpt-4o"
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
def validate_config() -> bool:
    """Validate that required configuration is present."""
    errors = []
    
    if not OPENAI_API_KEY and not OPENROUTER_API_KEY and not GROQ_API_KEY:
        errors.append("One of OPENAI_API_KEY, OPENROUTER_API_KEY, or GROQ_API_KEY is required")
    
    if USE_GROQ and not GROQ_API_KEY:
        errors.append("GROQ_API_KEY is required when USE_GROQ=true")
    
    if USE_OPENROUTER and not OPENROUTER_API_KEY:
        errors.append("OPENROUTER_API_KEY is required when USE_OPENROUTER=true")
    
    if not TAVILY_API_KEY:
        errors.append("TAVILY_API_KEY is required (for web search fallback)")
    
    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True

def get_config_summary() -> Dict[str, Any]:
    """Get a summary of current configuration."""
    if USE_GROQ:
        provider = "Groq"
    elif USE_OPENROUTER:
        provider = "OpenRouter"
    else:
        provider = "OpenAI"
    
    return {
        "api_provider": provider,
        "api_base_url": API_BASE_URL or "default",
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

# Validation is now optional - don't crash on import if API keys are missing
# This allows the app to start and serve basic endpoints like /health and /stats
# The actual API call endpoints will fail gracefully if keys are not configured
try:
    validate_config()
except ValueError as e:
    import warnings
    warnings.warn(f"Configuration warning: {e}")

