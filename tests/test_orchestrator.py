"""Tests for the Orchestrator component."""

import pytest
from src.orchestration.orchestrator import Orchestrator
from src.generation.rag_system import GeneratedAnswer
from src.database.supabase_client import ChunkKey, ChunkRecord
from src.ingestion.embedder import Embedding


class TestOrchestrator:
    """Test suite for RAG orchestration with LangGraph."""

    def test_answer_single_question_end_to_end(
        self, vector_db, mock_llm, mock_embeddings
    ):
        """Answer single question and return GeneratedAnswer with citations."""
        # Given
        vector_db.insert_chunk(ChunkRecord(
            key=ChunkKey("security-doc", "auth-section", 1),
            status="active",
            content="finanso supports OAuth 2.0 and SAML authentication methods.",
            embedding=Embedding(vector=[0.1] * 1024),
            metadata=None
        ))
        orchestrator = Orchestrator(client=vector_db, llm=mock_llm)

        # When
        result = orchestrator.answer("What authentication methods does finanso support?")

        # Then
        assert isinstance(result, GeneratedAnswer)
        assert result.answer == "This is a mock answer."
        assert len(result.citations) == 1
        assert result.citations[0].key.document_id == "security-doc"

    def test_handle_empty_retrieval_results(
        self, vector_db, mock_llm, mock_embeddings
    ):
        """Return graceful 'not found' response without LLM call."""
        # Given
        # Empty database - no chunks inserted
        orchestrator = Orchestrator(client=vector_db, llm=mock_llm)

        # When
        result = orchestrator.answer("What is the meaning of life?")

        # Then
        assert "cannot find" in result.answer.lower()
        assert result.citations == []
        assert mock_llm.last_prompt is None  # LLM was never called

    def test_handle_llm_failure_gracefully(
        self, vector_db, mock_embeddings
    ):
        """Raise appropriate error when LLM fails."""
        # Given
        vector_db.insert_chunk(ChunkRecord(
            key=ChunkKey("doc", "chunk", 1),
            status="active",
            content="Some content",
            embedding=Embedding(vector=[0.1] * 1024),
            metadata=None
        ))

        class FailingLLM:
            def invoke(self, prompt: str) -> str:
                raise RuntimeError("LLM service unavailable")

        orchestrator = Orchestrator(client=vector_db, llm=FailingLLM())

        # When / Then
        with pytest.raises(RuntimeError, match="LLM service unavailable"):
            orchestrator.answer("Any question?")

    def test_process_multiple_questions_as_batch(
        self, vector_db, mock_llm, mock_embeddings
    ):
        """Process questionnaire and return list of answers in order."""
        # Given
        vector_db.insert_chunk(ChunkRecord(
            key=ChunkKey("security-doc", "auth-section", 1),
            status="active",
            content="finanso supports OAuth 2.0 authentication.",
            embedding=Embedding(vector=[0.1] * 1024),
            metadata=None
        ))
        orchestrator = Orchestrator(client=vector_db, llm=mock_llm)
        questions = [
            "What authentication methods are supported?",
            "How is data encrypted?",
            "What certifications do you have?",
        ]

        # When
        results = orchestrator.process_questionnaire(questions)

        # Then
        assert len(results) == 3
        assert all(isinstance(r, GeneratedAnswer) for r in results)

    @pytest.mark.skip(reason="Deferred to Phase 6 - LangGraph state not needed for basic orchestration")
    def test_state_flows_through_langgraph_nodes(self):
        """Verify state contains retrieved chunks before generation."""
        pass
