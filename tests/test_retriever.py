"""
Tests for the Retriever module.

Tests similarity search functionality for finding relevant document chunks.
"""

import pytest
from src.retrieval.retriever import Retriever
from src.database.supabase_client import ChunkKey, ChunkRecord, SearchResult
from src.ingestion.embedder import Embedding


class TestRetriever:
    """Tests for retriever search functionality."""

    def test_search_returns_similar_chunks(self, mock_embeddings, vector_db):
        """Test that search returns chunks similar to the query."""
        # Given: Chunks indexed in database
        chunk = ChunkRecord(
            key=ChunkKey(document_id="doc-1", chunk_id="chunk-1", revision=1),
            status="active",
            content="MFA authentication requires two factors.",
            embedding=Embedding(vector=[0.1] * 1024),
            metadata=None
        )
        vector_db.insert_chunk(chunk)
        retriever = Retriever(client=vector_db)

        # When: Search for similar content
        results = retriever.search("How does MFA work?")

        # Then: Returns SearchResult with the chunk
        assert len(results) > 0
        assert isinstance(results[0], SearchResult)
        assert results[0].chunk.content == "MFA authentication requires two factors."
        assert 0.0 <= results[0].similarity <= 1.0

    def test_respects_top_k_limit(self, mock_embeddings, vector_db):
        """Test that search returns at most top_k results."""
        # Given: Many chunks indexed
        for i in range(10):
            chunk = ChunkRecord(
                key=ChunkKey(document_id="doc-1", chunk_id=f"chunk-{i}", revision=1),
                status="active",
                content=f"Content about topic {i}",
                embedding=Embedding(vector=[0.1] * 1024),
                metadata=None
            )
            vector_db.insert_chunk(chunk)
        retriever = Retriever(client=vector_db)

        # When: Search with top_k=3
        results = retriever.search("query", top_k=3)

        # Then: Returns at most 3 results
        assert len(results) == 3

    def test_only_returns_active_chunks(self, mock_embeddings, vector_db):
        """Test that search only returns active chunks, not superseded."""
        # Given: Active and superseded chunks
        active_chunk = ChunkRecord(
            key=ChunkKey(document_id="doc-1", chunk_id="chunk-1", revision=2),
            status="active",
            content="Current version",
            embedding=Embedding(vector=[0.1] * 1024),
            metadata=None
        )
        superseded_chunk = ChunkRecord(
            key=ChunkKey(document_id="doc-1", chunk_id="chunk-1", revision=1),
            status="superseded",
            content="Old version",
            embedding=Embedding(vector=[0.1] * 1024),
            metadata=None
        )
        # SQLiteClient handles unique constraints and superseding
        vector_db.insert_chunk(superseded_chunk)
        vector_db.insert_chunk(active_chunk)
        retriever = Retriever(client=vector_db)

        # When: Search
        results = retriever.search("query")

        # Then: Only active chunk returned
        assert len(results) == 1
        assert results[0].chunk.status == "active"
        assert results[0].chunk.content == "Current version"
