"""Tests for RunStore - manages runs and answers persistence."""

import pytest

from src.domain.models import Questionnaire, Question, Run, RunConfig, AnswerSuccess, RetrievedChunk, Citation, ChunkKey
from src.domain.run_store import RunStore
from src.domain.questionnaire_store import QuestionnaireStore
from src.database.sqlite_client import SQLiteClient


@pytest.fixture
def db_client():
    return SQLiteClient(db_path=":memory:")


@pytest.fixture
def store(db_client):
    """Provide a RunStore with an in-memory database."""
    return RunStore(db_client=db_client)


@pytest.fixture
def questionnaire_store(db_client):
    """Provide a QuestionnaireStore with the same database."""
    return QuestionnaireStore(db_client=db_client)


@pytest.fixture
def setup_questions(questionnaire_store):
    """Setup a questionnaire and questions to satisfy foreign keys."""
    q = Questionnaire(id="ikea", name="Ikea")
    questionnaire_store.save_questionnaire(q)
    questions = [
        Question(id="ikea:Q1.1", questionnaire_id="ikea", question_id="Q1.1", text="SOC 2?", sequence=1),
        Question(id="ikea:Q1.2", questionnaire_id="ikea", question_id="Q1.2", text="Audit?", sequence=2),
    ]
    questionnaire_store.save_questions(questions)


SAMPLE_CONFIG = RunConfig(
    id="config-001",
    name="Baseline llama3.2",
    llm_model="llama3.2",
    llm_temperature=0.7,
    retrieval_top_k=5,
    similarity_threshold=0.5,
    chunk_size=800,
    chunk_overlap=100,
    embedding_model="mxbai-embed-large",
    embedding_dimensions=1024,
    description="First experiment with default settings",
)

SAMPLE_RUN = Run(
    id="run-001",
    config=SAMPLE_CONFIG,
    name="Baseline llama3.2",
    status="active"
)

SAMPLE_ANSWER = AnswerSuccess(
    id="answer-001",
    run_id="run-001",
    question_id="ikea:Q1.1",
    answer_text="Yes, we are SOC 2 Type II certified [1].",
    retrieved_chunks=[
        RetrievedChunk(
            document_id="soc2-docs",
            chunk_id="chunk-001",
            revision=1,
            content="We maintain SOC 2 Type II certification...",
            similarity_score=0.92,
            rank=1,
        ),
        RetrievedChunk(
            document_id="security-policy",
            chunk_id="chunk-042",
            revision=1,
            content="Annual audits are performed...",
            similarity_score=0.85,
            rank=2,
        ),
    ],
    citations=[
        Citation(
            key=ChunkKey(document_id="soc2-docs", chunk_id="chunk-001", revision=1),
            content_snippet="We maintain SOC 2 Type II certification...",
        ),
    ],
)



class TestRunStore:
    """Test suite for RunStore."""

    def test_create_run_with_full_config(self, store):
        """Create a run with full configuration snapshot."""
        # Given

        # When
        store.save_run(SAMPLE_RUN)
        retrieved = store.get_run("run-001")

        # Then
        assert retrieved is not None
        assert retrieved.id == "run-001"
        assert retrieved.name == "Baseline llama3.2"
        assert retrieved.config.llm_model == "llama3.2"
        assert retrieved.config.llm_temperature == 0.7
        assert retrieved.config.retrieval_top_k == 5
        assert retrieved.config.similarity_threshold == 0.5
        assert retrieved.config.chunk_size == 800
        assert retrieved.config.chunk_overlap == 100
        assert retrieved.config.embedding_model == "mxbai-embed-large"
        assert retrieved.config.embedding_dimensions == 1024
        assert retrieved.status == "active"

    def test_save_answer_with_retrieved_chunks(self, store, setup_questions):
        """Save an answer with its retrieved chunks."""
        # Given
        store.save_run(SAMPLE_RUN)

        # When
        store.save_answer(SAMPLE_ANSWER)
        retrieved = store.get_answer("answer-001")

        # Then
        assert retrieved is not None
        assert retrieved.id == "answer-001"
        assert retrieved.run_id == "run-001"
        assert retrieved.question_id == "ikea:Q1.1"
        assert retrieved.answer_text == "Yes, we are SOC 2 Type II certified [1]."
        assert len(retrieved.retrieved_chunks) == 2
        assert retrieved.retrieved_chunks[0].similarity_score == 0.92
        assert retrieved.retrieved_chunks[1].document_id == "security-policy"

    def test_save_answer_with_citations(self, store, setup_questions):
        """Save an answer with its citations."""
        # Given
        store.save_run(SAMPLE_RUN)

        # When
        store.save_answer(SAMPLE_ANSWER)
        retrieved = store.get_answer("answer-001")

        # Then
        assert retrieved is not None
        assert len(retrieved.citations) == 1
        assert retrieved.citations[0].key.document_id == "soc2-docs"
        assert retrieved.citations[0].content_snippet == "We maintain SOC 2 Type II certification..."

    def test_get_all_answers_for_run(self, store, setup_questions):
        """Get all answers belonging to a specific run."""
        # Given
        store.save_run(SAMPLE_RUN)

        answer1 = AnswerSuccess(
            id="answer-001",
            run_id="run-001",
            question_id="ikea:Q1.1",
            answer_text="Answer to Q1.1",
        )
        answer2 = AnswerSuccess(
            id="answer-002",
            run_id="run-001",
            question_id="ikea:Q1.2",
            answer_text="Answer to Q1.2",
        )
        store.save_answer(answer1)
        store.save_answer(answer2)

        # When
        answers = store.get_answers_for_run("run-001")

        # Then
        assert len(answers) == 2
        assert {a.id for a in answers} == {"answer-001", "answer-002"}

    def test_get_answer_by_run_and_question(self, store, setup_questions):
        """Retrieve a specific answer by run ID and question ID."""
        # Given
        store.save_run(SAMPLE_RUN)
        store.save_answer(SAMPLE_ANSWER)

        # When
        retrieved = store.get_answer_by_run_and_question("run-001", "ikea:Q1.1")

        # Then
        assert retrieved is not None
        assert retrieved.id == "answer-001"
        assert retrieved.run_id == "run-001"
        assert retrieved.question_id == "ikea:Q1.1"

    def test_list_runs_by_status(self, store):
        """List runs filtered by status."""
        # Given
        config = RunConfig(
            id="cfg-1", name="name", llm_model="m", llm_temperature=0.7,
            retrieval_top_k=5, similarity_threshold=0.5, chunk_size=800,
            chunk_overlap=100, embedding_model="e", embedding_dimensions=1024
        )
        run1 = Run(
            id="run-active",
            config=config,
            name="Active Run",
            status="active",
        )
        run2 = Run(
            id="run-archived",
            config=config,
            name="Archived Run",
            status="archived",
        )
        store.save_run(run1)
        store.save_run(run2)

        # When
        active_runs = store.list_runs_by_status("active")
        archived_runs = store.list_runs_by_status("archived")

        # Then
        assert len(active_runs) == 1
        assert active_runs[0].id == "run-active"
        assert len(archived_runs) == 1
        assert archived_runs[0].id == "run-archived"
