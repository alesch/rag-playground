"""
Integration tests for embedder.

Tests embedding text via Ollama using mxbai-embed-large model.
"""

import pytest
from src.ingestion.embedder import generate_embedding, generate_embeddings, Embedding


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


def test_generate_embeddings_maintains_order():
    """Test that batch embedding maintains the order of input texts."""
    # Given
    texts = [
        "First chunk about authentication.",
        "Second chunk about encryption.",
        "Third chunk about access control."
    ]

    # When
    embeddings = generate_embeddings(texts)

    # Then
    assert len(embeddings) == 3, "Should return same number of embeddings as input texts"
    assert all(isinstance(e, Embedding) for e in embeddings), "All should be Embedding objects"

    # And: Verify order by comparing with individual embedding
    individual_embedding = generate_embedding(texts[1])
    assert embeddings[1] == individual_embedding, "Order must be maintained"


def test_raise_error_when_ollama_unavailable():
    """Test that appropriate error is raised when Ollama service is unavailable."""
    # Given
    text = "Test text for embedding."
    
    # Temporarily change to unreachable address to simulate Ollama being unavailable
    import src.ingestion.embedder as embedder
    original_url = embedder.OLLAMA_API_URL
    embedder.OLLAMA_API_URL = "http://127.0.0.1:9999/api/embeddings"  # Valid but unreachable port
    
    try:
        # When/Then
        with pytest.raises(ConnectionError) as exc_info:
            generate_embedding(text)
        
        # Verify error message is helpful
        assert "Failed to connect to Ollama" in str(exc_info.value)
        assert "Is Ollama running?" in str(exc_info.value)
    finally:
        # Restore original URL
        embedder.OLLAMA_API_URL = original_url


def test_reject_empty_text():
    """Test that empty text is rejected with ValueError."""
    # When/Then - Test empty string
    with pytest.raises(ValueError) as exc_info:
        generate_embedding("")
    assert "Text cannot be empty" in str(exc_info.value)
    
    # When/Then - Test whitespace-only string
    with pytest.raises(ValueError) as exc_info:
        generate_embedding("   ")
    assert "Text cannot be empty" in str(exc_info.value)
    
    # When/Then - Test newline-only string
    with pytest.raises(ValueError) as exc_info:
        generate_embedding("\n\n")
    assert "Text cannot be empty" in str(exc_info.value)
