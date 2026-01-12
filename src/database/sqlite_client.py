"""
SQLite implementation of the vector database client.
Uses sqlite-vec for vector similarity search.
"""

import json
import sqlite3
import sqlite_vec
import struct
from typing import Dict, Any, List, Optional
from src.config import SQLITE_DB_PATH, EMBEDDING_DIMENSIONS
from src.database.base import VectorDatabaseClient, ChunkKey, ChunkRecord, SearchResult
from src.ingestion.embedder import Embedding


class SQLiteClient(VectorDatabaseClient):
    """Client for SQLite database operations with vector support."""

    def __init__(self, db_path: str = str(SQLITE_DB_PATH)):
        """Initialize SQLite connection and load sqlite-vec extension."""
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Enable foreign key support
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # Load sqlite-vec extension
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)
        
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        cursor = self.conn.cursor()
        
        # Vector Table (existing)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT,
                chunk_id TEXT,
                revision INTEGER,
                status TEXT,
                content TEXT,
                metadata TEXT,
                UNIQUE(document_id, chunk_id, revision)
            )
        """)
        
        # Virtual table for vector search (existing)
        cursor.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS vec_document_chunks USING vec0(
                embedding float[{EMBEDDING_DIMENSIONS}]
            )
        """)
        
        # Domain: Questionnaires
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questionnaires (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                source_file TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Domain: Questions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                questionnaire_id TEXT REFERENCES questionnaires(id) ON DELETE CASCADE,
                question_id TEXT NOT NULL,
                text TEXT NOT NULL,
                section TEXT,
                sequence INTEGER DEFAULT 0
            )
        """)
        
        # Domain: Runs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS run_configurations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                llm_model TEXT,
                llm_temperature REAL,
                retrieval_top_k INTEGER,
                similarity_threshold REAL,
                chunk_size INTEGER,
                chunk_overlap INTEGER,
                embedding_model TEXT,
                embedding_dimensions INTEGER,
                description TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                run_configuration_id TEXT REFERENCES run_configurations(id),
                name TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Domain: Answers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                id TEXT PRIMARY KEY,
                run_id TEXT REFERENCES runs(id) ON DELETE CASCADE,
                question_id TEXT REFERENCES questions(id),
                is_success BOOLEAN NOT NULL,
                answer_text TEXT,
                error_message TEXT,
                retrieved_chunks_json TEXT,
                meta_json TEXT
            )
        """)
        
        # Domain: Citations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS citations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                answer_id TEXT REFERENCES answers(id) ON DELETE CASCADE,
                document_id TEXT,
                chunk_id TEXT,
                revision INTEGER,
                content_snippet TEXT
            )
        """)
        
        # Domain: Retrieved Chunks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS retrieved_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                answer_id TEXT REFERENCES answers(id) ON DELETE CASCADE,
                document_id TEXT,
                chunk_id TEXT,
                revision INTEGER,
                content TEXT,
                similarity_score REAL,
                rank INTEGER
            )
        """)
        
        self.conn.commit()

    def is_connected(self) -> bool:
        """Check if connection is open."""
        try:
            self.conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    def insert_chunk(self, chunk_record: ChunkRecord) -> Dict[str, Any]:
        """Insert a single chunk."""
        return self.batch_insert_chunks([chunk_record])[0]

    def batch_insert_chunks(self, chunk_records: List[ChunkRecord]) -> List[Dict[str, Any]]:
        """Batch insert multiple chunks."""
        cursor = self.conn.cursor()
        results = []

        for record in chunk_records:
            # Handle status: supersede previous active revisions if this one is active
            if record.status == "active":
                cursor.execute("""
                    UPDATE document_chunks 
                    SET status = 'superseded' 
                    WHERE document_id = ? AND chunk_id = ? AND status = 'active'
                """, (record.key.document_id, record.key.chunk_id))

            # Insert into main table
            cursor.execute("""
                INSERT OR REPLACE INTO document_chunks 
                (document_id, chunk_id, revision, status, content, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                record.key.document_id,
                record.key.chunk_id,
                record.key.revision,
                record.status,
                record.content,
                json.dumps(record.metadata) if record.metadata else None
            ))
            
            rowid = cursor.lastrowid
            
            # Insert into vector table using same rowid
            # sqlite-vec's vec0 uses rowid automatically if not specified, 
            # but we want to ensure they match.
            cursor.execute("""
                INSERT OR REPLACE INTO vec_document_chunks (rowid, embedding)
                VALUES (?, ?)
            """, (rowid, sqlite_vec.serialize_float32(record.embedding.vector)))
            
            results.append({
                "document_id": record.key.document_id,
                "chunk_id": record.key.chunk_id,
                "revision": record.key.revision
            })

        self.conn.commit()
        return results

    def delete_chunk(self, key: ChunkKey) -> None:
        """Delete a specific chunk."""
        cursor = self.conn.cursor()
        # Find the rowid first to delete from both tables
        cursor.execute("""
            SELECT id FROM document_chunks 
            WHERE document_id = ? AND chunk_id = ? AND revision = ?
        """, (key.document_id, key.chunk_id, key.revision))
        row = cursor.fetchone()
        
        if row:
            rowid = row['id']
            cursor.execute("DELETE FROM document_chunks WHERE id = ?", (rowid,))
            cursor.execute("DELETE FROM vec_document_chunks WHERE rowid = ?", (rowid,))
            self.conn.commit()

    def get_chunk_revisions(self, document_id: str, chunk_id: str) -> Dict[int, ChunkRecord]:
        """Get all revisions for a specific chunk."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.*, v.embedding 
            FROM document_chunks c
            JOIN vec_document_chunks v ON c.id = v.rowid
            WHERE c.document_id = ? AND c.chunk_id = ?
        """, (document_id, chunk_id))
        
        rows = cursor.fetchall()
        return {row['revision']: self._row_to_record(row) for row in rows}

    def query_chunks_by_status(self, document_id: str, status: str) -> List[ChunkRecord]:
        """Query chunks filtered by document_id and status."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.*, v.embedding 
            FROM document_chunks c
            JOIN vec_document_chunks v ON c.id = v.rowid
            WHERE c.document_id = ? AND c.status = ?
        """, (document_id, status))
        
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def search_by_embedding(
        self,
        query_embedding: Embedding,
        top_k: int = 5,
        threshold: float = 0.0,
        status: str = "active"
    ) -> List[SearchResult]:
        """Search for similar chunks by embedding using L2 distance."""
        cursor = self.conn.cursor()
        
        # sqlite-vec uses distance functions. vec_distance_L2 is common.
        # We need to convert distance to similarity if we want to respect threshold.
        # For now, let's just return top_k.
        
        cursor.execute(f"""
            SELECT 
                c.*, 
                v.embedding,
                vec_distance_L2(v.embedding, ?) as distance
            FROM vec_document_chunks v
            JOIN document_chunks c ON v.rowid = c.id
            WHERE c.status = ?
            ORDER BY distance ASC
            LIMIT ?
        """, (sqlite_vec.serialize_float32(query_embedding.vector), status, top_k))
        
        results = []
        for row in cursor.fetchall():
            # Rough conversion from L2 distance to a "similarity" score
            # (Higher is better, 1.0 is perfect)
            distance = row['distance']
            similarity = 1.0 / (1.0 + distance)
            
            if similarity >= threshold:
                results.append(SearchResult(
                    chunk=self._row_to_record(row),
                    similarity=similarity
                ))
                
        return results

    def _deserialize_embedding(self, blob: bytes) -> List[float]:
        """Deserialize a binary blob into a list of floats."""
        # Each float32 is 4 bytes
        count = len(blob) // 4
        return list(struct.unpack(f"{count}f", blob))

    def _row_to_record(self, row: sqlite3.Row) -> ChunkRecord:
        """Convert a SQLite row to a ChunkRecord."""
        # sqlite-vec returns embeddings as blobs
        embedding_vector = self._deserialize_embedding(row['embedding'])
        
        return ChunkRecord(
            key=ChunkKey(
                document_id=row['document_id'],
                chunk_id=row['chunk_id'],
                revision=row['revision']
            ),
            status=row['status'],
            content=row['content'],
            embedding=Embedding(vector=embedding_vector),
            metadata=json.loads(row['metadata']) if row['metadata'] else None
        )
