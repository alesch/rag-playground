"""Tests for the Orchestrator component."""

import pytest
from src.orchestration.orchestrator import Orchestrator
from src.generation.generator import GeneratedAnswer
from src.database.supabase_client import ChunkKey, ChunkRecord
from src.ingestion.embedder import Embedding


class TestOrchestrator:
    """Test suite for RAG orchestration with LangGraph."""

    def test_answer_single_question_end_to_end(
        self, mock_supabase_client, mock_llm, mock_embeddings
    ):
        """Answer single question and return GeneratedAnswer with citations."""
        # Given
        mock_supabase_client.insert_chunk(ChunkRecord(
            key=ChunkKey("security-doc", "auth-section", 1),
            status="active",
            content="finanso supports OAuth 2.0 and SAML authentication methods.",
            embedding=Embedding(vector=[0.1] * 1024),
            metadata=None
        ))
        orchestrator = Orchestrator(client=mock_supabase_client, llm=mock_llm)

        # When
        result = orchestrator.answer("What authentication methods does finanso support?")

        # Then
        assert isinstance(result, GeneratedAnswer)
        assert result.answer == "This is a mock answer."
        assert len(result.citations) == 1
        assert result.citations[0].key.document_id == "security-doc"

    @pytest.mark.skip(reason="Not implemented yet")
    def test_handle_empty_retrieval_results(self):
        """Return graceful 'not found' response without LLM call."""
        pass

    @pytest.mark.skip(reason="Not implemented yet")
    def test_handle_llm_failure_gracefully(self):
        """Raise appropriate error when LLM fails."""
        pass

    @pytest.mark.skip(reason="Not implemented yet")
    def test_process_multiple_questions_as_batch(self):
        """Process questionnaire and return list of answers in order."""
        pass

    @pytest.mark.skip(reason="Not implemented yet")
    def test_state_flows_through_langgraph_nodes(self):
        """Verify state contains retrieved chunks before generation."""
        pass
