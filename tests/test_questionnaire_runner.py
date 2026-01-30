"""Tests for QuestionnaireRunner - coordinates questionnaire execution."""

import pytest
from unittest.mock import MagicMock

from src.domain.questionnaire_runner import QuestionnaireRunner
from src.domain.models import Questionnaire, Question, Run, RunConfig, ChunkKey, AnswerSuccess, AnswerFailure
from src.generation.generator import GeneratedAnswer, Citation as GenCitation
from src.domain.questionnaire_store import QuestionnaireStore
from src.domain.run_store import RunStore
from src.database.sqlite_client import SQLiteClient


@pytest.fixture
def db_client():
    return SQLiteClient(db_path=":memory:")


@pytest.fixture
def mock_orchestrator():
    return MagicMock()


@pytest.fixture
def questionnaire_store(db_client):
    store = QuestionnaireStore(db_client=db_client)
    q = Questionnaire(id="test-q", name="Test Questionnaire")
    store.save_questionnaire(q)
    store.save_questions([
        Question(id="test-q:Q1", questionnaire_id="test-q", question_id="Q1", text="What is your security policy?", sequence=1),
        Question(id="test-q:Q2", questionnaire_id="test-q", question_id="Q2", text="Do you use encryption?", sequence=2),
    ])
    return store


@pytest.fixture
def run_store(db_client):
    return RunStore(db_client=db_client)


@pytest.fixture
def run_config():
    config = RunConfig(
        id="config-001",
        name="Test Run Config",
        llm_model="llama3.2",
        llm_temperature=0.7,
        retrieval_top_k=5,
        similarity_threshold=0.5,
        chunk_size=800,
        chunk_overlap=100,
        embedding_model="mxbai-embed-large",
        embedding_dimensions=1024,
    )
    return Run(
        id="run-001",
        config=config,
        name="Test Run"
    )


class TestQuestionnaireRunner:
    """Test suite for QuestionnaireRunner."""

    def test_run_full_questionnaire(self, mock_orchestrator, questionnaire_store, run_store, run_config):
        """Run a full questionnaire and verify answers are saved."""
        # Given
        runner = QuestionnaireRunner(
            orchestrator=mock_orchestrator,
            questionnaire_store=questionnaire_store,
            run_store=run_store
        )
        
        # Mock orchestrator response
        mock_orchestrator.answer.side_effect = [
            GeneratedAnswer(
                answer="We have a strong security policy.",
                citations=[GenCitation(key=ChunkKey(document_id="doc1", chunk_id="c1", revision=1), content_snippet="Policy details...")],
            ),
            GeneratedAnswer(
                answer="Yes, we use AES-256.",
                citations=[],
            )
        ]

        # When
        runner.run_questionnaire(questionnaire_id="test-q", run=run_config)

        # Then
        answers = run_store.get_answers_for_run(run_config.id)
        assert len(answers) == 2
        
        # Verify first answer
        ans1 = next(a for a in answers if a.question_id == "test-q:Q1")
        assert isinstance(ans1, AnswerSuccess)
        assert "security policy" in ans1.answer_text
        assert len(ans1.citations) == 1
        assert ans1.citations[0].key.document_id == "doc1"
        
        # Verify second answer
        ans2 = next(a for a in answers if a.question_id == "test-q:Q2")
        assert isinstance(ans2, AnswerSuccess)
        assert "AES-256" in ans2.answer_text
        
        # Verify run was also saved
        assert run_store.get_run(run_config.id) is not None

    def test_handle_generation_error(self, mock_orchestrator, questionnaire_store, run_store, run_config):
        """Handle errors during generation by creating an AnswerFailure."""
        # Given
        runner = QuestionnaireRunner(
            orchestrator=mock_orchestrator,
            questionnaire_store=questionnaire_store,
            run_store=run_store
        )
        
        # Mock orchestrator to raise an error
        mock_orchestrator.answer.side_effect = RuntimeError("LLM failure")

        # When
        runner.run_questionnaire(questionnaire_id="test-q", run=run_config)

        # Then
        answers = run_store.get_answers_for_run(run_config.id)
        assert len(answers) == 2
        
        for ans in answers:
            assert isinstance(ans, AnswerFailure)
            assert ans.error_message == "LLM failure"
            assert ans.question_id in ["test-q:Q1", "test-q:Q2"]