"""Tests for Retrieved Chunks Normalization - moving chunks from JSON to relational table."""

import pytest
from src.domain.models import Run, RunConfig, AnswerSuccess, RetrievedChunk, Questionnaire, Question
from src.domain.run_store import RunStore
from src.domain.questionnaire_store import QuestionnaireStore

@pytest.fixture
def store(vector_db):
    return RunStore(db_client=vector_db)

@pytest.fixture
def questionnaire_store(vector_db):
    return QuestionnaireStore(db_client=vector_db)

def test_retrieved_chunks_stored_in_normalized_table(vector_db, store, questionnaire_store):
    """Verify that retrieved chunks are stored in the retrieved_chunks table."""
    # Given
    q = Questionnaire(id="ikea", name="Ikea")
    questionnaire_store.save_questionnaire(q)
    
    question = Question(id="ikea:Q1", questionnaire_id="ikea", question_id="Q1", text="Test?")
    questionnaire_store.save_questions([question])
    
    config = RunConfig(
        id="cfg-1", name="name", llm_model="m", llm_temperature=0.7,
        retrieval_top_k=5, similarity_threshold=0.5, chunk_size=800,
        chunk_overlap=100, embedding_model="e", embedding_dimensions=1024
    )
    run = Run(id="run-1", config=config, name="Run 1")
    store.save_run(run)

    answer = AnswerSuccess(
        id="ans-1",
        run_id="run-1",
        question_id="ikea:Q1",
        answer_text="Answer text",
        retrieved_chunks=[
            RetrievedChunk(
                document_id="doc-1",
                chunk_id="chunk-1",
                revision=1,
                content="Chunk content",
                similarity_score=0.9,
                rank=1
            )
        ]
    )
    
    # When
    store.save_answer(answer)
    
    # Then
    cursor = vector_db.conn.cursor()
    # We expect this table to exist and contain the chunk
    cursor.execute("SELECT * FROM retrieved_chunks WHERE answer_id = ?", ("ans-1",))
    rows = cursor.fetchall()
    
    assert len(rows) == 1
    assert rows[0]['document_id'] == "doc-1"
    assert rows[0]['chunk_id'] == "chunk-1"
    assert rows[0]['content'] == "Chunk content"
    assert rows[0]['similarity_score'] == 0.9
    assert rows[0]['rank'] == 1
