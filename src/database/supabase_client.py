"""
Supabase client for database operations.

DEPRECATED: Use SQLiteClient instead. Supabase support is maintained for legacy
compatibility but SQLite is the primary database for development and production.

Handles connection to Supabase and operations on document_chunks table.
"""

import json
from supabase import create_client, Client
from typing import Dict, Any, Optional, List, cast
from src.config import SUPABASE_URL, SUPABASE_KEY, CHUNKS_TABLE
from src.ingestion.embedder import Embedding
from src.database.base import VectorDatabaseClient, ChunkKey, ChunkRecord, SearchResult


class SupabaseClient(VectorDatabaseClient):
    """Client for Supabase database operations."""
    
    def __init__(self):
        """
        Initialize Supabase client with credentials from config.
        
        Raises:
            ValueError: If credentials are not configured
        """
        if not SUPABASE_URL:
            raise ValueError("SUPABASE_URL not configured")
        if not SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY not configured")
        
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.table_name = CHUNKS_TABLE
    
    def is_connected(self) -> bool:
        """
        Check if client is connected to Supabase.
        
        Attempts a simple query to verify the connection.
        
        Returns:
            True if connected and can query the table, False otherwise
        """
        try:
            self.client.table(self.table_name).select("id").limit(1).execute()
            return True
        except Exception:
            return False
    
    def _prepare_chunk_data(self, chunk_record: ChunkRecord) -> Dict[str, Any]:
        """
        Prepare chunk data for database insertion.
        
        Args:
            chunk_record: ChunkRecord containing all chunk data
            
        Returns:
            Dictionary formatted for database insertion
        """
        return {
            "document_id": chunk_record.key.document_id,
            "chunk_id": chunk_record.key.chunk_id,
            "revision": chunk_record.key.revision,
            "status": chunk_record.status,
            "content": chunk_record.content,
            "embedding": chunk_record.embedding.vector,
            "metadata": chunk_record.metadata
        }
    
    def insert_chunk(self, chunk_record: ChunkRecord) -> Dict[str, Any]:
        """
        Insert a chunk with content, embedding, revision, and status.

        If the new chunk is active, marks any previous active revisions
        of the same document_id/chunk_id as superseded.

        Args:
            chunk_record: ChunkRecord containing all chunk data

        Returns:
            Dictionary containing the inserted chunk data
        """
        # Mark previous active revisions as superseded if inserting an active chunk
        if chunk_record.status == "active":
            self.client.table(self.table_name).update(
                {"status": "superseded"}
            ).eq(
                "document_id", chunk_record.key.document_id
            ).eq(
                "chunk_id", chunk_record.key.chunk_id
            ).eq(
                "status", "active"
            ).execute()

        data = self._prepare_chunk_data(chunk_record)
        response = self.client.table(self.table_name).insert(data).execute()
        return response.data[0]
    
    def batch_insert_chunks(self, chunk_records: List[ChunkRecord]) -> List[Dict[str, Any]]:
        """
        Batch insert multiple chunks efficiently.

        For active chunks, marks any previous active revisions
        of the same document_id/chunk_id as superseded.

        Args:
            chunk_records: List of ChunkRecord objects

        Returns:
            List of dictionaries containing the inserted chunk data
        """
        # Supersede previous active revisions for all active chunks
        active_chunks = [cr for cr in chunk_records if cr.status == "active"]
        for chunk_record in active_chunks:
            self.client.table(self.table_name).update(
                {"status": "superseded"}
            ).eq(
                "document_id", chunk_record.key.document_id
            ).eq(
                "chunk_id", chunk_record.key.chunk_id
            ).eq(
                "status", "active"
            ).execute()

        # Batch insert all chunks
        data = [self._prepare_chunk_data(chunk_record) for chunk_record in chunk_records]
        response = self.client.table(self.table_name).insert(data).execute()
        return response.data
    
    def delete_chunk(self, key: ChunkKey) -> None:
        """
        Delete a specific chunk by its composite key.

        Args:
            key: ChunkKey containing the composite key fields
        """
        self.client.table(self.table_name).delete().eq(
            "document_id", key.document_id
        ).eq(
            "chunk_id", key.chunk_id
        ).eq(
            "revision", key.revision
        ).execute()

    def get_chunk_revisions(self, document_id: str, chunk_id: str) -> Dict[int, ChunkRecord]:
        """
        Get all revisions for a specific chunk.

        Args:
            document_id: The document ID
            chunk_id: The chunk ID

        Returns:
            Dictionary keyed by revision number containing ChunkRecord objects
        """
        response = self.client.table(self.table_name).select("*").eq(
            "document_id", document_id
        ).eq(
            "chunk_id", chunk_id
        ).execute()

        rows = cast(List[Dict[str, Any]], response.data)
        return {row["revision"]: self._row_to_chunk_record(row) for row in rows}

    def _row_to_chunk_record(self, row: Dict[str, Any]) -> ChunkRecord:
        """
        Convert a database row to a ChunkRecord.

        Args:
            row: Dictionary containing database row data

        Returns:
            ChunkRecord reconstructed from the row
        """
        # Embedding may be returned as JSON string from Supabase
        embedding_data = row["embedding"]
        if isinstance(embedding_data, str):
            embedding_data = json.loads(embedding_data)

        return ChunkRecord(
            key=ChunkKey(
                document_id=row["document_id"],
                chunk_id=row["chunk_id"],
                revision=row["revision"]
            ),
            status=row["status"],
            content=row["content"],
            embedding=Embedding(vector=embedding_data),
            metadata=row.get("metadata")
        )

    def query_chunks_by_status(self, document_id: str, status: str) -> List[ChunkRecord]:
        """
        Query chunks filtered by document_id and status.

        Args:
            document_id: The document ID to filter by
            status: The status to filter by (e.g., "active", "superseded")

        Returns:
            List of ChunkRecord objects matching the criteria
        """
        response = self.client.table(self.table_name).select("*").eq(
            "document_id", document_id
        ).eq(
            "status", status
        ).execute()

        rows = cast(List[Dict[str, Any]], response.data)
        return [self._row_to_chunk_record(row) for row in rows]

    def search_by_embedding(
        self,
        query_embedding: Embedding,
        top_k: int = 5,
        threshold: float = 0.0,
        status: str = "active"
    ) -> List[SearchResult]:
        """
        Search for chunks similar to the query embedding using pgvector.

        Args:
            query_embedding: The query embedding to search for
            top_k: Maximum number of results to return
            threshold: Minimum similarity score (0.0 to 1.0)
            status: Filter by chunk status (default: "active")

        Returns:
            List of SearchResult objects, sorted by similarity descending
        """
        response = self.client.rpc(
            "search_chunks",
            {
                "query_embedding": query_embedding.vector,
                "max_results": top_k,
                "similarity_threshold": threshold,
                "status_filter": status
            }
        ).execute()

        rows = cast(List[Dict[str, Any]], response.data)
        return [
            SearchResult(chunk=self._row_to_chunk_record(row), similarity=row["similarity"])
            for row in rows
        ]
