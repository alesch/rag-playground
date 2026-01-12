"""Tests for Retrieved Chunks Normalization."""

import pytest
from src.domain.models import Questionnaire, Question, Run, RunConfig, AnswerSuccess, RetrievedChunk
from src.domain.run_store import RunStore
from src.domain.questionnaire_store import QuestionnaireStore
from src.database.sqlite_client import SQLiteClient

@pytest.fixture
def db_client():
    return SQLiteClient(db_path=":memory:")

@pytest.fixture
def store(db_client):
    return RunStore(db_client=db_client)

@pytest.fixture
def questionnaire_store(db_client):
    return QuestionnaireStore(db_client=db_client)

@pytest.fixture
def setup_context(store, questionnaire_store):
    """Setup a questionnaire, question, and run."""
    q = Questionnaire(id="ikea", name="Ikea")
    questionnaire_store.save_questionnaire(q)
    
    question = Question(id="ikea:Q1.1", questionnaire_id="ikea", question_id="Q1.1", text="SOC 2?", sequence=1)
    questionnaire_store.save_questions([question])
    
    config = RunConfig(
        id="cfg-1", name="name", llm_model="m", llm_temperature=0.7,
        retrieval_top_k=5, similarity_threshold=0.5, chunk_size=800,
        chunk_overlap=100, embedding_model="e", embedding_dimensions=1024
    )
    run = Run(id="run-001", config=config, name="Test Run", status="active")
    store.save_run(run)
    return run, question

def test_retrieved_chunks_are_stored_in_normalized_table(store, db_client, setup_context):
    """RED: Verify that saving an answer results in records in the retrieved_chunks table."""
    # Given
    run, question = setup_context
    answer = AnswerSuccess(
        id="answer-001",
        run_id=run.id,
        question_id=question.id,
        answer_text="Yes, we are SOC 2 certified.",
        retrieved_chunks=[
            RetrievedChunk(
                document_id="doc-1",
                chunk_id="c-1",
                revision=1,
                content="SOC 2 content",
                similarity_score=0.9,
                rank=1
            )
        ]
    )

    # When
    store.save_answer(answer)

    # Then
    cursor = db_client.conn.cursor()
    # This should fail because the table does not exist yet
    cursor.execute("SELECT * FROM retrieved_chunks WHERE answer_id = ?", (answer.id,))
    rows = cursor.fetchall()
    
    assert len(rows) == 1
    assert rows[0]["document_id"] == "doc-1"
    assert rows[0]["chunk_id"] == "c-1"
    assert rows[0]["similarity_score"] == 0.9
    assert rows[0]["rank"] == 1
