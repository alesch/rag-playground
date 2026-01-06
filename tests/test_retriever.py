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

    def test_search_returns_similar_chunks(self, mock_embeddings, mock_supabase_client):
        """Test that search returns chunks similar to the query."""
        # Given: Chunks indexed in database
        chunk = ChunkRecord(
            key=ChunkKey(document_id="doc-1", chunk_id="chunk-1", revision=1),
            status="active",
            content="MFA authentication requires two factors.",
            embedding=Embedding(vector=[0.1] * 1024),
            metadata=None
        )
        mock_supabase_client.insert_chunk(chunk)
        retriever = Retriever(client=mock_supabase_client)

        # When: Search for similar content
        results = retriever.search("How does MFA work?")

        # Then: Returns SearchResult with the chunk
        assert len(results) > 0
        assert isinstance(results[0], SearchResult)
        assert results[0].chunk.content == "MFA authentication requires two factors."
        assert 0.0 <= results[0].similarity <= 1.0
