"""
Shared pytest fixtures for all tests.
"""

import pytest
from src.ingestion.embedder import Embedding
from src.database.supabase_client import ChunkKey, ChunkRecord


from src.database.sqlite_client import SQLiteClient
from tests.mocks import MockLLM, fake_generate_embedding, fake_generate_embeddings


def pytest_addoption(parser):
    """Add command line option to run slow tests."""
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )


def pytest_collection_modifyitems(config, items):
    """Skip slow tests unless --run-slow is specified."""
    if config.getoption("--run-slow"):
        return
    
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture
def vector_db():
    """Provide an in-memory SQLiteClient for fast tests."""
    return SQLiteClient(db_path=":memory:")


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
