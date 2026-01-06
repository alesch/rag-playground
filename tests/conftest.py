"""
Shared pytest fixtures for all tests.
"""

import pytest
from src.ingestion.embedder import Embedding
from src.database.supabase_client import ChunkKey, ChunkRecord


from tests.mocks import MockSupabaseClient, MockLLM, fake_generate_embedding, fake_generate_embeddings


@pytest.fixture
def mock_supabase_client():
    """Provide an in-memory mock SupabaseClient for fast tests."""
    return MockSupabaseClient()


@pytest.fixture
def mock_embeddings(monkeypatch):
    """
    Mock embedding functions for faster tests.

    Returns deterministic fake embeddings (1024 dimensions of 0.1).
    Use this fixture in tests that don't need real embeddings.
    """
    monkeypatch.setattr(
        "src.ingestion.embedder.generate_embedding",
        fake_generate_embedding
    )
    monkeypatch.setattr(
        "src.ingestion.embedder.generate_embeddings",
        fake_generate_embeddings
    )
    # Also patch where it's imported in other modules
    monkeypatch.setattr(
        "scripts.ingest_corpus.generate_embeddings",
        fake_generate_embeddings
    )
    monkeypatch.setattr(
        "src.retrieval.retriever.generate_embedding",
        fake_generate_embedding
    )


@pytest.fixture
def mock_llm():
    """Provide a mock LLM for fast tests."""
    return MockLLM()
