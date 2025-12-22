"""
Integration tests for embedder.

Tests embedding text via Ollama using mxbai-embed-large model.
"""

import pytest
from src.ingestion.embedder import generate_embedding, batch_embed, Embedding


def test_generate_embedding_via_ollama():
    """Test that text is embedded into 1024-dimensional vector via Ollama."""
    # Given
    text = "Multi-factor authentication is required for all user accounts."
    
    # When
    embedding = generate_embedding(text)
    
    # Then
    assert isinstance(embedding, Embedding), "Should return an Embedding object"
    assert len(embedding) == 1024, "mxbai-embed-large produces 1024-dimensional embeddings"
    assert all(isinstance(x, float) for x in embedding.vector), "All values should be floats"


def test_batch_embed_maintains_order():
    """Test that batch embedding maintains the order of input texts."""
    # Given
    texts = [
        "First chunk about authentication.",
        "Second chunk about encryption.",
        "Third chunk about access control."
    ]
    
    # When
    batch_embeddings = batch_embed(texts)
    
    # Then
    assert len(batch_embeddings) == 3, "Should return same number of embeddings as input texts"
    assert all(isinstance(e, Embedding) for e in batch_embeddings), "All should be Embedding objects"
    
    # Verify order: generate individual embedding for second text and compare
    individual_embedding = generate_embedding(texts[1])
    assert batch_embeddings[1] == individual_embedding, "Order must be maintained: second batch embedding should match second text"
