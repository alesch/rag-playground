"""
Integration tests for embedder.

Tests embedding text via Ollama using mxbai-embed-large model.
"""

import pytest
from src.ingestion.embedder import generate_embedding, Embedding


def test_generate_embedding_via_ollama():
    """Test that text is embedded into 1024-dimensional vector via Ollama."""
    # Given
    text = "Multi-factor authentication is required for all user accounts."
    
    # When
    embedding = generate_embedding(text)
    
    # Then
    assert isinstance(embedding, Embedding), "Should return an Embedding object"
    assert len(embedding.vector) == 1024, "mxbai-embed-large produces 1024-dimensional embeddings"
    assert all(isinstance(x, float) for x in embedding.vector), "All values should be floats"
