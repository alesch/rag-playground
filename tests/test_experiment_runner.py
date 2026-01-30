"""Tests for ExperimentRunner - orchestrates multiple experiment trials."""

import pytest
from unittest.mock import MagicMock
from src.domain.models import Questionnaire, Question, Run, RunConfig, ChunkKey
from src.domain.questionnaire_store import QuestionnaireStore
from src.domain.run_store import RunStore
from src.database.sqlite_client import SQLiteClient
from src.generation.rag_system import GeneratedAnswer, Citation as GenCitation
from src.evaluation.evaluation_store import EvaluationStore
from scripts.run_experiments import ExperimentRunner


@pytest.fixture
def db_client():
    return SQLiteClient(db_path=":memory:")


@pytest.fixture
def mock_orchestrator():
    return MagicMock()


@pytest.fixture
def questionnaire_store(db_client):
    store = QuestionnaireStore(db_client=db_client)
    q = Questionnaire(id="exp-q", name="Experiment Questionnaire")
    store.save_questionnaire(q)
    
    # Create 3 questions for initial testing
    questions = [
        Question(
            id=f"exp-q:Q{i}",
            questionnaire_id="exp-q",
            question_id=f"Q{i}",
            text=f"Question {i}?",
            sequence=i
        )
        for i in range(1, 4)
    ]
    store.save_questions(questions)
    return store


@pytest.fixture
def run_store(db_client):
    return RunStore(db_client=db_client)


@pytest.fixture
def evaluation_store(db_client):
    return EvaluationStore(db_client=db_client)


@pytest.fixture
def ground_truth_run(run_store, questionnaire_store):
    """Create a ground truth run with baseline answers."""
    config = RunConfig(
        id="gt-config",
        name="Ground Truth Config",
        llm_model="llama3.2",
        llm_temperature=0.8,
        retrieval_top_k=5,
        similarity_threshold=0.0,
        chunk_size=800,
        chunk_overlap=100,
        embedding_model="mxbai-embed-large",
        embedding_dimensions=1024,
    )
    run = Run(id="gt-run", config=config, name="Ground Truth")
    run_store.save_run(run)
    
    # Save ground truth answers
    questions = questionnaire_store.get_questions("exp-q")
    for q in questions:
        from src.domain.models import AnswerSuccess
        answer = AnswerSuccess(
            id=f"ans-gt-run-{q.question_id}",
            run_id="gt-run",
            question_id=q.id,
            answer_text=f"Ground truth answer for {q.question_id}",
            citations=[]
        )
        answer.save_on(run_store)
    
    return run


class TestExperimentRunner:
    """Test suite for ExperimentRunner."""
    
    def test_evaluation_performed_and_metrics_returned(
        self, mock_orchestrator, questionnaire_store, run_store,
        evaluation_store, ground_truth_run, mock_embeddings
    ):
        """Verify evaluation is performed and mean_answer_relevancy is returned."""
        # Given
        runner = ExperimentRunner(
            orchestrator=mock_orchestrator,
            questionnaire_store=questionnaire_store,
            run_store=run_store,
            evaluation_store=evaluation_store
        )
        
        mock_orchestrator.answer.side_effect = [
            GeneratedAnswer(answer="Answer 1", citations=[]),
            GeneratedAnswer(answer="Answer 2", citations=[]),
            GeneratedAnswer(answer="Answer 3", citations=[])
        ]
        
        config = RunConfig(
            id="exp-config-eval",
            name="Eval Test Config",
            llm_model="llama3.2",
            llm_temperature=0.5,
            retrieval_top_k=5,
            similarity_threshold=0.0,
            chunk_size=800,
            chunk_overlap=100,
            embedding_model="mxbai-embed-large",
            embedding_dimensions=1024,
        )
        
        # When
        result = runner.run_experiment(
            questionnaire_id="exp-q",
            ground_truth_run_id="gt-run",
            config=config
        )
        
        # Then
        assert "mean_answer_relevancy" in result
        assert isinstance(result["mean_answer_relevancy"], float)
        assert 0.0 <= result["mean_answer_relevancy"] <= 1.0
    
    def test_orchestrator_called_and_answers_saved(
        self, mock_orchestrator, questionnaire_store, run_store,
        evaluation_store, ground_truth_run, mock_embeddings
    ):
        """Verify orchestrator is called for each question and answers are saved."""
        # Given
        runner = ExperimentRunner(
            orchestrator=mock_orchestrator,
            questionnaire_store=questionnaire_store,
            run_store=run_store,
            evaluation_store=evaluation_store
        )
        
        mock_orchestrator.answer.side_effect = [
            GeneratedAnswer(
                answer="Answer 1",
                citations=[GenCitation(
                    key=ChunkKey(document_id="doc1", chunk_id="c1", revision=1),
                    content_snippet="snippet 1"
                )]
            ),
            GeneratedAnswer(
                answer="Answer 2",
                citations=[]
            ),
            GeneratedAnswer(
                answer="Answer 3",
                citations=[]
            )
        ]
        
        config = RunConfig(
            id="exp-config-1",
            name="Test Config 1",
            llm_model="llama3.2",
            llm_temperature=0.5,
            retrieval_top_k=5,
            similarity_threshold=0.1,
            chunk_size=800,
            chunk_overlap=100,
            embedding_model="mxbai-embed-large",
            embedding_dimensions=1024,
        )
        
        # When
        result = runner.run_experiment(
            questionnaire_id="exp-q",
            ground_truth_run_id="gt-run",
            config=config
        )
        
        # Then
        assert mock_orchestrator.answer.call_count == 3
        
        # And
        answers = run_store.get_answers_for_run(result["run_id"])
        assert len(answers) == 3
        
        from src.domain.models import AnswerSuccess
        assert all(isinstance(a, AnswerSuccess) for a in answers)
        assert answers[0].answer_text == "Answer 1"
        assert answers[1].answer_text == "Answer 2"
        assert answers[2].answer_text == "Answer 3"
    
    def test_happy_path_single_experiment(
        self, mock_orchestrator, questionnaire_store, run_store, 
        evaluation_store, ground_truth_run, mock_embeddings
    ):
        """Run single experiment with 3 questions and verify results."""
        # Given
        runner = ExperimentRunner(
            orchestrator=mock_orchestrator,
            questionnaire_store=questionnaire_store,
            run_store=run_store,
            evaluation_store=evaluation_store
        )
        
        mock_orchestrator.answer.side_effect = [
            GeneratedAnswer(
                answer="Answer 1",
                citations=[GenCitation(
                    key=ChunkKey(document_id="doc1", chunk_id="c1", revision=1),
                    content_snippet="snippet"
                )]
            ),
            GeneratedAnswer(
                answer="Answer 2",
                citations=[]
            ),
            GeneratedAnswer(
                answer="Answer 3",
                citations=[]
            )
        ]
        
        config = RunConfig(
            id="exp-config-1",
            name="Test Config 1",
            llm_model="llama3.2",
            llm_temperature=0.5,
            retrieval_top_k=5,
            similarity_threshold=0.1,
            chunk_size=800,
            chunk_overlap=100,
            embedding_model="mxbai-embed-large",
            embedding_dimensions=1024,
        )
        
        # When
        result = runner.run_experiment(
            questionnaire_id="exp-q",
            ground_truth_run_id="gt-run",
            config=config
        )
        
        # Then
        assert result["run_id"] is not None
        assert result["questions_answered"] == 3
        assert result["success"] is True
