"""
Document embedder for generating vector embeddings via Ollama.

Uses mxbai-embed-large model to generate 1024-dimensional embeddings.
"""

from dataclasses import dataclass
from typing import List
import requests


# Constants
OLLAMA_API_URL = "http://127.0.0.1:11434/api/embeddings"
EMBEDDING_MODEL = "mxbai-embed-large"
EXPECTED_DIMENSIONS = 1024


@dataclass
class Embedding:
    """Represents a 1024-dimensional embedding vector."""
    
    vector: List[float]
    
    def __post_init__(self):
        """Validate embedding dimensions."""
        if len(self.vector) != EXPECTED_DIMENSIONS:
            raise ValueError(
                f"Expected {EXPECTED_DIMENSIONS} dimensions, got {len(self.vector)}"
            )


def generate_embedding(text: str) -> Embedding:
    """
    Generate a 1024-dimensional embedding for text via Ollama.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding object with 1024-dimensional vector
        
    Raises:
        ValueError: If text is empty
        requests.exceptions.ConnectionError: If Ollama service is unavailable
        requests.exceptions.HTTPError: If Ollama returns an error
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": EMBEDDING_MODEL, "prompt": text},
            timeout=30
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(
            f"Failed to connect to Ollama at {OLLAMA_API_URL}. "
            "Is Ollama running?"
        ) from e
    
    vector = response.json()["embedding"]
    return Embedding(vector=vector)
