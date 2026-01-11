"""Tests for RunStore - manages runs and answers persistence."""

import pytest

from src.domain.models import Run, AnswerSuccess, RetrievedChunk, Citation, ChunkKey
from src.domain.run_store import RunStore


SAMPLE_RUN = Run(
    id="run-001",
    name="Baseline llama3.2",
    description="First experiment with default settings",
    llm_model="llama3.2",
    llm_temperature=0.7,
    retrieval_top_k=5,
    similarity_threshold=0.5,
    chunk_size=800,
    chunk_overlap=100,
    embedding_model="mxbai-embed-large",
    embedding_dimensions=1024,
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

    def test_create_run_with_full_config(self):
        """Create a run with full configuration snapshot."""
        # Given
        store = RunStore()

        # When
        store.save_run(SAMPLE_RUN)
        retrieved = store.get_run("run-001")

        # Then
        assert retrieved is not None
        assert retrieved.id == "run-001"
        assert retrieved.name == "Baseline llama3.2"
        assert retrieved.llm_model == "llama3.2"
        assert retrieved.llm_temperature == 0.7
        assert retrieved.retrieval_top_k == 5
        assert retrieved.similarity_threshold == 0.5
        assert retrieved.chunk_size == 800
        assert retrieved.chunk_overlap == 100
        assert retrieved.embedding_model == "mxbai-embed-large"
        assert retrieved.embedding_dimensions == 1024
        assert retrieved.status == "active"

    def test_save_answer_with_retrieved_chunks(self):
        """Save an answer with its retrieved chunks."""
        # Given
        store = RunStore()
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

    def test_save_answer_with_citations(self):
        """Save an answer with its citations."""
        # Given
        store = RunStore()
        store.save_run(SAMPLE_RUN)

        # When
        store.save_answer(SAMPLE_ANSWER)
        retrieved = store.get_answer("answer-001")

        # Then
        assert retrieved is not None
        assert len(retrieved.citations) == 1
        assert retrieved.citations[0].key.document_id == "soc2-docs"
        assert retrieved.citations[0].content_snippet == "We maintain SOC 2 Type II certification..."

    def test_get_all_answers_for_run(self):
        """Get all answers belonging to a specific run."""
        # Given
        store = RunStore()
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

    def test_get_answer_by_run_and_question(self):
        """Retrieve a specific answer by run ID and question ID."""
        # Given
        store = RunStore()
        store.save_run(SAMPLE_RUN)
        store.save_answer(SAMPLE_ANSWER)

        # When
        retrieved = store.get_answer_by_run_and_question("run-001", "ikea:Q1.1")

        # Then
        assert retrieved is not None
        assert retrieved.id == "answer-001"
        assert retrieved.run_id == "run-001"
        assert retrieved.question_id == "ikea:Q1.1"

    def test_list_runs_by_status(self):
        """List runs filtered by status."""
        # Given
        store = RunStore()
        run1 = Run(
            id="run-active",
            name="Active Run",
            llm_model="model",
            llm_temperature=0.7,
            retrieval_top_k=5,
            similarity_threshold=0.5,
            chunk_size=800,
            chunk_overlap=100,
            embedding_model="embed",
            embedding_dimensions=1024,
            status="active",
        )
        run2 = Run(
            id="run-archived",
            name="Archived Run",
            llm_model="model",
            llm_temperature=0.7,
            retrieval_top_k=5,
            similarity_threshold=0.5,
            chunk_size=800,
            chunk_overlap=100,
            embedding_model="embed",
            embedding_dimensions=1024,
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
