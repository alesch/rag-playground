"""Tests for RunStore with RunConfig."""

import pytest
from src.domain.models import Run, RunConfig, AnswerSuccess, RetrievedChunk, Citation, ChunkKey
from src.domain.stores.run_store import RunStore
from src.infrastructure.database.sqlite_client import SQLiteClient

@pytest.fixture
def store():
    """Provide a RunStore with an in-memory database."""
    db_client = SQLiteClient(db_path=":memory:")
    return RunStore(db_client=db_client)

@pytest.fixture
def run_config():
    return RunConfig(
        id="config-001",
        name="Baseline Llama 3.2",
        llm_model="llama3.2",
        llm_temperature=0.7,
        retrieval_top_k=5,
        similarity_threshold=0.5,
        chunk_size=800,
        chunk_overlap=100,
        embedding_model="mxbai-embed-large",
        embedding_dimensions=1024,
        description="Standard config"
    )

@pytest.fixture
def sample_run(run_config):
    return Run(
        id="run-001",
        config=run_config,
        status="active"
    )

class TestRunStoreConfig:
    """Test suite for RunStore with RunConfig separation."""

    def test_save_and_retrieve_run_with_config(self, store, run_config, sample_run):
        """Save a run with its configuration and retrieve it."""
        # Given
        # We might need to save config explicitly first, or let save_run handle it?
        # Let's assume explicit save for strict flexibility/reusability
        store.save_config(run_config)
        store.save_run(sample_run)

        # When
        retrieved_run = store.get_run("run-001")

        # Then
        assert retrieved_run is not None
        assert retrieved_run.id == "run-001"
        assert retrieved_run.config.id == "config-001"
        assert retrieved_run.config.llm_model == "llama3.2"
        assert retrieved_run.status == "active"

    def test_reuse_config_across_runs(self, store, run_config):
        """Verify multiple runs can share the same config."""
        # Given
        store.save_config(run_config)
        
        run1 = Run(id="run-A", config=run_config)
        run2 = Run(id="run-B", config=run_config)
        
        # When
        store.save_run(run1)
        store.save_run(run2)
        
        # Then
        r1 = store.get_run("run-A")
        r2 = store.get_run("run-B")
        
        assert r1.config.id == r2.config.id
        assert r1.config.llm_model == "llama3.2"
