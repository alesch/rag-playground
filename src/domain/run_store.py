"""Storage for runs and answers."""

import json
from typing import Optional

from src.domain.models import Run, RunConfig, Answer, AnswerSuccess, AnswerFailure, RetrievedChunk, Citation, ChunkKey
from src.database.sqlite_client import SQLiteClient


class RunStore:
    """Manages run and answer persistence."""

    def __init__(self, db_client: SQLiteClient):
        self.db_client = db_client
        self.conn = db_client.conn

    def save_config(self, config: RunConfig) -> None:
        """Save a run configuration."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO run_configurations (
                    id, name, llm_model, llm_temperature, retrieval_top_k,
                    similarity_threshold, chunk_size, chunk_overlap,
                    embedding_model, embedding_dimensions, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                config.id, config.name, config.llm_model, config.llm_temperature,
                config.retrieval_top_k, config.similarity_threshold,
                config.chunk_size, config.chunk_overlap,
                config.embedding_model, config.embedding_dimensions,
                config.description
            ))
            self.conn.commit()
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                # If config exists with same ID, we verify it matches (in strict mode) 
                # or just pass (idempotent). For now, pass.
                pass
            else:
                raise

    def get_config(self, id: str) -> Optional[RunConfig]:
        """Retrieve a run configuration by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM run_configurations WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            return None
        return RunConfig(
            id=row['id'],
            name=row['name'],
            llm_model=row['llm_model'],
            llm_temperature=row['llm_temperature'],
            retrieval_top_k=row['retrieval_top_k'],
            similarity_threshold=row['similarity_threshold'],
            chunk_size=row['chunk_size'],
            chunk_overlap=row['chunk_overlap'],
            embedding_model=row['embedding_model'],
            embedding_dimensions=row['embedding_dimensions'],
            description=row['description']
        )

    def save_run(self, run: Run) -> None:
        """Save a run. Raises ValueError if ID already exists."""
        cursor = self.conn.cursor()
        
        # Ensure config exists
        self.save_config(run.config)

        try:
            cursor.execute("""
                INSERT INTO runs (id, run_configuration_id, name, status)
                VALUES (?, ?, ?, ?)
            """, (
                run.id,
                run.config.id,
                run.name,
                run.status
            ))
            self.conn.commit()
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(f"Run '{run.id}' already exists")
            raise

    def get_run(self, id: str) -> Optional[Run]:
        """Retrieve a run by ID."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                r.id as run_id, r.name as run_name, r.status as run_status,
                rc.id as config_id, rc.name as config_name, rc.llm_model, 
                rc.llm_temperature, rc.retrieval_top_k, rc.similarity_threshold,
                rc.chunk_size, rc.chunk_overlap, rc.embedding_model, 
                rc.embedding_dimensions, rc.description
            FROM runs r
            JOIN run_configurations rc ON r.run_configuration_id = rc.id
            WHERE r.id = ?
        """, (id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_run(row)

    def save_answer(self, answer: Answer) -> None:
        """Save an answer."""
        cursor = self.conn.cursor()
        
        is_success = isinstance(answer, AnswerSuccess)
        
        answer_text = None
        error_message = None
        citations_json = None
        retrieved_chunks_json = None
        meta_json = None
        
        if is_success:
            answer_text = answer.answer_text
            citations_json = json.dumps([
                {
                    "key": {
                        "document_id": c.key.document_id,
                        "chunk_id": c.key.chunk_id,
                        "revision": c.key.revision
                    },
                    "content_snippet": c.content_snippet
                } for c in answer.citations
            ])
            retrieved_chunks_json = json.dumps([
                {
                    "document_id": c.document_id,
                    "chunk_id": c.chunk_id,
                    "revision": c.revision,
                    "content": c.content,
                    "similarity_score": c.similarity_score,
                    "rank": c.rank
                } for c in answer.retrieved_chunks
            ])
            meta_json = json.dumps({
                "query_embedding": answer.query_embedding,
                "generation_time_ms": answer.generation_time_ms
            })
        else:
            error_message = answer.error_message

        cursor.execute("""
            INSERT OR REPLACE INTO answers 
            (id, run_id, question_id, is_success, answer_text, error_message, 
             citations_json, retrieved_chunks_json, meta_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            answer.id,
            answer.run_id,
            answer.question_id,
            is_success,
            answer_text,
            error_message,
            citations_json,
            retrieved_chunks_json,
            meta_json
        ))
        self.conn.commit()

    def get_answer(self, id: str) -> Optional[Answer]:
        """Retrieve an answer by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM answers WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_answer(row)

    def get_answers_for_run(self, run_id: str) -> list[Answer]:
        """Retrieve all answers for a specific run."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM answers WHERE run_id = ?", (run_id,))
        return [self._row_to_answer(row) for row in cursor.fetchall()]

    def get_answer_by_run_and_question(self, run_id: str, question_id: str) -> Optional[Answer]:
        """Retrieve a specific answer by run ID and question ID."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM answers 
            WHERE run_id = ? AND question_id = ?
        """, (run_id, question_id))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_answer(row)

    def list_runs_by_status(self, status: str) -> list[Run]:
        """List runs filtered by status."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                r.id as run_id, r.name as run_name, r.status as run_status,
                rc.id as config_id, rc.name as config_name, rc.llm_model, 
                rc.llm_temperature, rc.retrieval_top_k, rc.similarity_threshold,
                rc.chunk_size, rc.chunk_overlap, rc.embedding_model, 
                rc.embedding_dimensions, rc.description
            FROM runs r
            JOIN run_configurations rc ON r.run_configuration_id = rc.id
            WHERE r.status = ?
        """, (status,))
        
        return [self._row_to_run(row) for row in cursor.fetchall()]

    def _row_to_run(self, row) -> Run:
        """Convert a database row to a Run with its RunConfig."""
        config = RunConfig(
            id=row['config_id'],
            name=row['config_name'],
            llm_model=row['llm_model'],
            llm_temperature=row['llm_temperature'],
            retrieval_top_k=row['retrieval_top_k'],
            similarity_threshold=row['similarity_threshold'],
            chunk_size=row['chunk_size'],
            chunk_overlap=row['chunk_overlap'],
            embedding_model=row['embedding_model'],
            embedding_dimensions=row['embedding_dimensions'],
            description=row['description']
        )
        
        return Run(
            id=row['run_id'],
            config=config,
            status=row['run_status'],
            name=row['run_name']
        )

    def _row_to_answer(self, row) -> Answer:
        """Convert a database row to an AnswerSuccess or AnswerFailure."""
        if row['is_success']:
            citations = []
            if row['citations_json']:
                for c in json.loads(row['citations_json']):
                    citations.append(Citation(
                        key=ChunkKey(**c['key']),
                        content_snippet=c['content_snippet']
                    ))
            
            retrieved_chunks = []
            if row['retrieved_chunks_json']:
                for c in json.loads(row['retrieved_chunks_json']):
                    retrieved_chunks.append(RetrievedChunk(**c))
            
            meta = json.loads(row['meta_json']) if row['meta_json'] else {}
            
            return AnswerSuccess(
                id=row['id'],
                run_id=row['run_id'],
                question_id=row['question_id'],
                answer_text=row['answer_text'],
                retrieved_chunks=retrieved_chunks,
                citations=citations,
                query_embedding=meta.get('query_embedding'),
                generation_time_ms=meta.get('generation_time_ms')
            )
        else:
            return AnswerFailure(
                id=row['id'],
                run_id=row['run_id'],
                question_id=row['question_id'],
                error_message=row['error_message']
            )