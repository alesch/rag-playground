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
