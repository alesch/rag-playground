"""Tests for ExperimentRunner - orchestrates multiple experiment trials."""

import pytest
from unittest.mock import MagicMock
from src.domain.models import Questionnaire, Question, Run, RunConfig, ChunkKey
from src.domain.stores.questionnaire_store import QuestionnaireStore
from src.domain.stores.run_store import RunStore
from src.infrastructure.database.sqlite_client import SQLiteClient
from src.rag.rag_system import GeneratedAnswer, Citation as GenCitation
from src.domain.stores.evaluation_store import EvaluationStore
from src.experiments.run_experiments import ExperimentRunner


@pytest.fixture
def db_client():
    return SQLiteClient(db_path=":memory:")


@pytest.fixture
def mock_llm():
    """Mock LLM that returns predictable responses."""
    mock = MagicMock()
    mock.invoke.return_value = "Answer from mock LLM"
    return mock


@pytest.fixture
def mock_rag_system(db_client, mock_llm):
    """Create a RAGSystem with mock LLM for testing."""
    from src.rag.rag_system import RAGSystem
    return RAGSystem(
        client=db_client,
        llm=mock_llm,
        top_k=5,
        similarity_threshold=0.0
    )


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
        self, db_client, questionnaire_store, run_store,
        evaluation_store, ground_truth_run, mock_embeddings, mock_rag_system
    ):
        """Verify evaluation is performed and mean_answer_relevancy is returned."""
        # Given
        runner = ExperimentRunner(
            db_client=db_client,
            questionnaire_store=questionnaire_store,
            run_store=run_store,
            evaluation_store=evaluation_store,
            rag_system=mock_rag_system
        )
        
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
    
    def test_rag_system_called_and_answers_saved(
        self, db_client, questionnaire_store, run_store,
        evaluation_store, ground_truth_run, mock_embeddings, mock_llm, mock_rag_system
    ):
        """Verify RAG system is called for each question and answers are saved."""
        # Given
        # Add a chunk to database so retrieval returns results
        from src.infrastructure.database.supabase_client import ChunkRecord, ChunkKey
        from src.rag.ingestion.embedder import Embedding
        db_client.insert_chunk(ChunkRecord(
            key=ChunkKey("test-doc", "chunk1", 1),
            status="active",
            content="Test content for retrieval",
            embedding=Embedding(vector=[0.1] * 1024),
            metadata=None
        ))
        
        runner = ExperimentRunner(
            db_client=db_client,
            questionnaire_store=questionnaire_store,
            run_store=run_store,
            evaluation_store=evaluation_store,
            rag_system=mock_rag_system
        )
        
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
        assert mock_llm.invoke.call_count == 3
        
        # And
        answers = run_store.get_answers_for_run(result["run_id"])
        assert len(answers) == 3
        
        from src.domain.models import AnswerSuccess
        assert all(isinstance(a, AnswerSuccess) for a in answers)
        assert all(a.answer_text == "Answer from mock LLM" for a in answers)
    
    def test_retry_on_llm_failure(
        self, db_client, questionnaire_store, run_store,
        evaluation_store, ground_truth_run, mock_embeddings, mock_llm
    ):
        """Verify retry logic - fails 2 times then succeeds on 3rd attempt."""
        # Given
        # Add chunk so retrieval succeeds
        from src.infrastructure.database.sqlite_client import ChunkRecord, ChunkKey
        from src.rag.ingestion.embedder import Embedding
        db_client.insert_chunk(ChunkRecord(
            key=ChunkKey("test-doc", "chunk1", 1),
            status="active",
            content="Test content",
            embedding=Embedding(vector=[0.1] * 1024),
            metadata=None
        ))
        
        # Mock LLM to fail twice, then succeed
        mock_llm.invoke.side_effect = [
            RuntimeError("LLM timeout"),  # Q1 attempt 1
            RuntimeError("LLM timeout"),  # Q1 attempt 2
            "Answer 1",  # Q1 attempt 3 - success
            "Answer 2",  # Q2 attempt 1 - success
            "Answer 3",  # Q3 attempt 1 - success
        ]
        
        from src.rag.rag_system import RAGSystem
        rag_system = RAGSystem(
            client=db_client,
            llm=mock_llm,
            top_k=5,
            similarity_threshold=0.0
        )
        
        runner = ExperimentRunner(
            db_client=db_client,
            questionnaire_store=questionnaire_store,
            run_store=run_store,
            evaluation_store=evaluation_store,
            rag_system=rag_system
        )
        
        config = RunConfig(
            id="exp-config-retry",
            name="Retry Test Config",
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
        assert mock_llm.invoke.call_count == 5  # 3 for Q1, 1 for Q2, 1 for Q3
        assert result["questions_answered"] == 3
        assert result["success"] is True
    
    def test_run_multiple_experiments(
        self, db_client, questionnaire_store, run_store,
        evaluation_store, ground_truth_run, mock_embeddings, mock_rag_system
    ):
        """Run 2 configs × 2 trials = 4 experiments total."""
        # Given
        # Add chunk for retrieval
        from src.infrastructure.database.sqlite_client import ChunkRecord, ChunkKey
        from src.rag.ingestion.embedder import Embedding
        db_client.insert_chunk(ChunkRecord(
            key=ChunkKey("test-doc", "chunk1", 1),
            status="active",
            content="Test content",
            embedding=Embedding(vector=[0.1] * 1024),
            metadata=None
        ))
        
        runner = ExperimentRunner(
            db_client=db_client,
            questionnaire_store=questionnaire_store,
            run_store=run_store,
            evaluation_store=evaluation_store,
            rag_system=mock_rag_system
        )
        
        configs = [
            RunConfig(
                id="config-A",
                name="Config A",
                llm_model="llama3.2",
                llm_temperature=0.5,
                retrieval_top_k=5,
                similarity_threshold=0.0,
                chunk_size=800,
                chunk_overlap=100,
                embedding_model="mxbai-embed-large",
                embedding_dimensions=1024,
            ),
            RunConfig(
                id="config-B",
                name="Config B",
                llm_model="llama3.2",
                llm_temperature=0.7,
                retrieval_top_k=5,
                similarity_threshold=0.0,
                chunk_size=800,
                chunk_overlap=100,
                embedding_model="mxbai-embed-large",
                embedding_dimensions=1024,
            )
        ]
        
        # When
        results = runner.run_experiments(
            questionnaire_id="exp-q",
            ground_truth_run_id="gt-run",
            configs=configs,
            trials_per_config=2
        )
        
        # Then
        assert len(results) == 2  # 2 configs
        assert "config-A" in results
        assert "config-B" in results
        
        # And each config has 2 trials
        assert len(results["config-A"]["trials"]) == 2
        assert len(results["config-B"]["trials"]) == 2
        
        # And all trials succeeded
        for config_id in ["config-A", "config-B"]:
            for trial in results[config_id]["trials"]:
                assert trial["success"] is True
                assert trial["questions_answered"] == 3
    
    def test_happy_path_single_experiment(
        self, db_client, questionnaire_store, run_store, 
        evaluation_store, ground_truth_run, mock_embeddings, mock_rag_system
    ):
        """Run single experiment with 3 questions and verify results."""
        # Given
        runner = ExperimentRunner(
            db_client=db_client,
            questionnaire_store=questionnaire_store,
            run_store=run_store,
            evaluation_store=evaluation_store,
            rag_system=mock_rag_system
        )
        
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
