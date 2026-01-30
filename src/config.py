"""
Centralized configuration management for the Complaila RAG system.

This module loads environment variables and defines configuration parameters
for all components of the system.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# ============================================================================
# Logging Configuration
# ============================================================================

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Single logger for all modules
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("complaila")

# Suppress noisy library logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# ============================================================================
# Supabase Configuration
# ============================================================================

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

# ============================================================================
# Ollama Configuration
# ============================================================================

OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "mxbai-embed-large")
OLLAMA_CHAT_MODEL: str = os.getenv("OLLAMA_CHAT_MODEL", "llama3.2")

# LLM Temperature (optimized for llama3.2)
# Lower temperature = more deterministic, higher quality answers
# Performance tuning showed 0.3 optimal for llama3.2 (vs default 0.8)
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))

# Embedding dimensions for mxbai-embed-large
EMBEDDING_DIMENSIONS: int = 1024

# ============================================================================
# Retrieval Configuration (optimized for llama3.2)
# ============================================================================

# Similarity threshold for filtering retrieved chunks
# Performance tuning showed 0.3 optimal for llama3.2 (filters low-quality matches)
# Higher values = more strict filtering (may miss relevant context)
# Lower values = more permissive (may include irrelevant chunks)
SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))

# Number of chunks to retrieve for context
# Performance tuning showed 5 is optimal balance for llama3.2
# More chunks = more context but potential noise
RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))

# ============================================================================
# Document Ingestion Configuration
# ============================================================================

# Path to corpus documents
CORPUS_PATH: Path = PROJECT_ROOT / "data" / "corpus"

# Chunking parameters
CHUNK_SIZE: int = 800  # Target tokens per chunk (500-1000 range)
CHUNK_OVERLAP: int = 100  # Overlap between chunks to maintain context
MIN_CHUNK_SIZE: int = 100  # Minimum chunk size to avoid too-small fragments

# ============================================================================
# Database Configuration
# ============================================================================

# Database provider: "sqlite" or "supabase"
DB_PROVIDER: str = os.getenv("DB_PROVIDER", "sqlite")

# SQLite configuration
SQLITE_DB_PATH: Path = Path(os.getenv("SQLITE_DB_PATH", str(PROJECT_ROOT / "data" / "complaila.db")))

# Table name for storing document chunks
CHUNKS_TABLE: str = "document_chunks"

# Batch size for database operations
DB_BATCH_SIZE: int = 50

# ============================================================================
# Validation
# ============================================================================

def validate_config() -> bool:
    """
    Validate that all required configuration is present and valid.
    
    Returns:
        True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    errors = []
    
    # Provider-specific database validation
    if DB_PROVIDER == "supabase":
        if not SUPABASE_URL or SUPABASE_URL == "your_supabase_project_url":
            errors.append("SUPABASE_URL not configured for supabase provider")
        if not SUPABASE_KEY or SUPABASE_KEY == "your_supabase_anon_key":
            errors.append("SUPABASE_KEY not configured for supabase provider")
    elif DB_PROVIDER == "sqlite":
        # Ensure data directory exists
        SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    else:
        errors.append(f"Invalid DB_PROVIDER: {DB_PROVIDER}. Must be 'sqlite' or 'supabase'")
    
    # Check corpus path exists
    if not CORPUS_PATH.exists():
        errors.append(f"Corpus path does not exist: {CORPUS_PATH}")
    
    # Check chunking parameters
    if CHUNK_SIZE < MIN_CHUNK_SIZE:
        errors.append(f"CHUNK_SIZE ({CHUNK_SIZE}) must be >= MIN_CHUNK_SIZE ({MIN_CHUNK_SIZE})")
    
    if CHUNK_OVERLAP >= CHUNK_SIZE:
        errors.append(f"CHUNK_OVERLAP ({CHUNK_OVERLAP}) must be < CHUNK_SIZE ({CHUNK_SIZE})")
    
    if errors:
        raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True


if __name__ == "__main__":
    # Test configuration when run directly
    print("=== Complaila Configuration ===\n")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Corpus Path: {CORPUS_PATH}")
    print(f"\nSupabase URL: {SUPABASE_URL[:30]}...")
    print(f"Supabase Key: {'*' * 20}")
    print(f"\nOllama Base URL: {OLLAMA_BASE_URL}")
    print(f"Embedding Model: {OLLAMA_EMBEDDING_MODEL}")
    print(f"Chat Model: {OLLAMA_CHAT_MODEL}")
    print(f"Embedding Dimensions: {EMBEDDING_DIMENSIONS}")
    print(f"\nChunk Size: {CHUNK_SIZE}")
    print(f"Chunk Overlap: {CHUNK_OVERLAP}")
    print(f"Min Chunk Size: {MIN_CHUNK_SIZE}")
    print(f"\nDatabase Table: {CHUNKS_TABLE}")
    print(f"Batch Size: {DB_BATCH_SIZE}")
    print(f"\nLog Level: {LOG_LEVEL}")
    
    try:
        validate_config()
        print("\n✅ Configuration is valid!")
    except ValueError as e:
        print(f"\n❌ Configuration validation failed:\n{e}")
