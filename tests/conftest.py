"""
Shared pytest fixtures for all tests.
"""

import pytest
from src.ingestion.embedder import Embedding
from src.database.supabase_client import ChunkKey, ChunkRecord


class MockSupabaseClient:
    """In-memory mock of SupabaseClient for fast integration tests."""

    def __init__(self):
        self.chunks: dict[tuple[str, str, int], ChunkRecord] = {}

    def is_connected(self) -> bool:
        return True

    def insert_chunk(self, chunk_record: ChunkRecord) -> dict:
        if chunk_record.status == "active":
            self._supersede_previous(chunk_record.key)
        key = (chunk_record.key.document_id, chunk_record.key.chunk_id, chunk_record.key.revision)
        self.chunks[key] = chunk_record
        return {"document_id": chunk_record.key.document_id}

    def batch_insert_chunks(self, chunk_records: list[ChunkRecord]) -> list[dict]:
        for cr in chunk_records:
            if cr.status == "active":
                self._supersede_previous(cr.key)
        for cr in chunk_records:
            key = (cr.key.document_id, cr.key.chunk_id, cr.key.revision)
            self.chunks[key] = cr
        return [{"document_id": cr.key.document_id} for cr in chunk_records]

    def _supersede_previous(self, key: ChunkKey) -> None:
        for stored_key, record in self.chunks.items():
            if (stored_key[0] == key.document_id and
                stored_key[1] == key.chunk_id and
                record.status == "active"):
                self.chunks[stored_key] = ChunkRecord(
                    key=record.key,
                    status="superseded",
                    content=record.content,
                    embedding=record.embedding,
                    metadata=record.metadata
                )

    def delete_chunk(self, key: ChunkKey) -> None:
        stored_key = (key.document_id, key.chunk_id, key.revision)
        self.chunks.pop(stored_key, None)

    def query_chunks_by_status(self, document_id: str, status: str) -> list[ChunkRecord]:
        return [
            record for record in self.chunks.values()
            if record.key.document_id == document_id and record.status == status
        ]


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
    def fake_generate_embedding(text):
        # Return deterministic fake embedding
        return Embedding(vector=[0.1] * 1024)

    def fake_generate_embeddings(texts):
        return [fake_generate_embedding(text) for text in texts]

    monkeypatch.setattr(
        "src.ingestion.embedder.generate_embedding",
        fake_generate_embedding
    )
    monkeypatch.setattr(
        "src.ingestion.embedder.generate_embeddings",
        fake_generate_embeddings
    )
    # Also patch where it's imported in the ingest_corpus module
    monkeypatch.setattr(
        "scripts.ingest_corpus.generate_embeddings",
        fake_generate_embeddings
    )
