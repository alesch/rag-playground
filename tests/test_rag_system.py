"""
Tests for the RAGSystem module.

Tests answer generation using retrieved chunks and LLM.
"""

import pytest
from src.rag.rag_system import RAGSystem, GeneratedAnswer
from src.infrastructure.database.supabase_client import ChunkKey, ChunkRecord, SearchResult
from src.rag.ingestion.embedder import Embedding


class TestRAGSystem:
    """Tests for answer generation."""

    def test_generate_answer_from_retrieved_chunks(
        self, mock_embeddings, vector_db, mock_llm
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
        vector_db.insert_chunk(chunk)
        rag = RAGSystem(client=vector_db, llm=mock_llm)

        # When: Generate answer
        result = rag.answer("What is MFA?")

        # Then: Returns GeneratedAnswer with answer text
        assert isinstance(result, GeneratedAnswer)
        assert len(result.answer) > 0

    def test_answer_includes_citations(
        self, mock_embeddings, vector_db, mock_llm
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
        vector_db.insert_chunk(chunk)
        rag = RAGSystem(client=vector_db, llm=mock_llm)

        # When: Generate answer
        result = rag.answer("What is MFA?")

        # Then: Citations reference the source chunk
        assert len(result.citations) == 1
        assert result.citations[0].key.document_id == "doc-1"
        assert result.citations[0].key.chunk_id == "chunk-1"
        assert result.citations[0].key.revision == 1
        assert "MFA requires" in result.citations[0].content_snippet

    def test_handle_empty_retrieval_results(
        self, mock_embeddings, vector_db, mock_llm
    ):
        """Test that generator handles empty retrieval results gracefully."""
        # Given: No chunks in database
        rag = RAGSystem(client=vector_db, llm=mock_llm)

        # When: Generate answer
        result = rag.answer("What is MFA?")

        # Then: Returns answer with empty citations
        assert isinstance(result, GeneratedAnswer)
        assert len(result.citations) == 0

    def test_prompt_includes_all_context(
        self, mock_embeddings, vector_db, mock_llm
    ):
        """Test that prompt includes content from all retrieved chunks."""
        # Given: Multiple chunks indexed
        chunks = [
            ChunkRecord(
                key=ChunkKey(document_id="doc-1", chunk_id="chunk-1", revision=1),
                status="active",
                content="MFA requires two factors.",
                embedding=Embedding(vector=[0.1] * 1024),
                metadata=None
            ),
            ChunkRecord(
                key=ChunkKey(document_id="doc-1", chunk_id="chunk-2", revision=1),
                status="active",
                content="SSO enables single sign-on.",
                embedding=Embedding(vector=[0.1] * 1024),
                metadata=None
            ),
        ]
        for chunk in chunks:
            vector_db.insert_chunk(chunk)
        rag = RAGSystem(client=vector_db, llm=mock_llm)

        # When: Generate answer
        rag.answer("What is authentication?")

        # Then: Prompt includes all chunk content
        assert "MFA requires two factors" in mock_llm.last_prompt
        assert "SSO enables single sign-on" in mock_llm.last_prompt
