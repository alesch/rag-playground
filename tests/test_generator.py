"""
Tests for the Generator module.

Tests answer generation using retrieved chunks and LLM.
"""

import pytest
from src.generation.generator import Generator, GeneratedAnswer
from src.database.supabase_client import ChunkKey, ChunkRecord, SearchResult
from src.ingestion.embedder import Embedding


class TestGenerator:
    """Tests for answer generation."""

    def test_generate_answer_from_retrieved_chunks(
        self, mock_embeddings, mock_supabase_client, mock_llm
    ):
        """Test that generator produces an answer from retrieved chunks."""
        # Given: Chunks indexed in database
        chunk = ChunkRecord(
            key=ChunkKey(document_id="doc-1", chunk_id="chunk-1", revision=1),
            status="active",
            content="MFA requires two authentication factors.",
            embedding=Embedding(vector=[0.1] * 1024),
            metadata=None
        )
        mock_supabase_client.insert_chunk(chunk)
        generator = Generator(client=mock_supabase_client, llm=mock_llm)

        # When: Generate answer
        result = generator.generate("What is MFA?")

        # Then: Returns GeneratedAnswer with answer text
        assert isinstance(result, GeneratedAnswer)
        assert len(result.answer) > 0

    def test_answer_includes_citations(
        self, mock_embeddings, mock_supabase_client, mock_llm
    ):
        """Test that generated answer includes citations to source chunks."""
        # Given: Chunk indexed in database
        chunk = ChunkRecord(
            key=ChunkKey(document_id="doc-1", chunk_id="chunk-1", revision=1),
            status="active",
            content="MFA requires two authentication factors.",
            embedding=Embedding(vector=[0.1] * 1024),
            metadata=None
        )
        mock_supabase_client.insert_chunk(chunk)
        generator = Generator(client=mock_supabase_client, llm=mock_llm)

        # When: Generate answer
        result = generator.generate("What is MFA?")

        # Then: Citations reference the source chunk
        assert len(result.citations) == 1
        assert result.citations[0].key.document_id == "doc-1"
        assert result.citations[0].key.chunk_id == "chunk-1"
        assert result.citations[0].key.revision == 1
        assert "MFA requires" in result.citations[0].content_snippet

    def test_handle_empty_retrieval_results(
        self, mock_embeddings, mock_supabase_client, mock_llm
    ):
        """Test that generator handles empty retrieval results gracefully."""
        # Given: No chunks in database
        generator = Generator(client=mock_supabase_client, llm=mock_llm)

        # When: Generate answer
        result = generator.generate("What is MFA?")

        # Then: Returns answer with empty citations
        assert isinstance(result, GeneratedAnswer)
        assert len(result.citations) == 0
