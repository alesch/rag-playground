"""Tests for domain models factory methods."""

import pytest
from unittest.mock import Mock
from src.domain.models import AnswerSuccess, AnswerFailure, Question, Citation, ChunkKey

class TestDomainFactories:
    """Test suite for domain model factory methods."""

    def test_answer_success_factory(self):
        """Test creating AnswerSuccess from mocked GeneratedAnswer."""
        # Given
        question = Question(id="q1", questionnaire_id="qid", question_id="Q1", text="?")
        
        mock_citation = Mock()
        mock_citation.key.document_id = "doc1"
        mock_citation.key.chunk_id = "chk1"
        mock_citation.key.revision = 1
        mock_citation.content_snippet = "snippet"
        
        mock_generated = Mock()
        mock_generated.answer = "Success"
        mock_generated.citations = [mock_citation]

        # When
        answer = AnswerSuccess.from_GeneratedAnswer("run1", question, mock_generated)

        # Then
        assert isinstance(answer, AnswerSuccess)
        assert answer.id == "ans-run1-Q1"
        assert answer.answer_text == "Success"
        assert len(answer.citations) == 1
        assert answer.citations[0].key.document_id == "doc1"
        assert answer.citations[0].content_snippet == "snippet"

    def test_answer_failure_factory(self):
        """Test creating AnswerFailure from exception."""
        # Given
        question = Question(id="q1", questionnaire_id="qid", question_id="Q1", text="?")
        error = RuntimeError("Fail")

        # When
        answer = AnswerFailure.from_exception("run1", question, error)

        # Then
        assert isinstance(answer, AnswerFailure)
        assert answer.id == "ans-run1-Q1"
        assert answer.error_message == "Fail"
