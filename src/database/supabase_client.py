"""
Supabase client for database operations.

Handles connection to Supabase and operations on document_chunks table.
"""

from dataclasses import dataclass
from supabase import create_client, Client
from typing import Dict, Any, Optional, List
from src.config import SUPABASE_URL, SUPABASE_KEY, CHUNKS_TABLE
from src.ingestion.embedder import Embedding


@dataclass
class ChunkKey:
    """Represents the composite key for a chunk."""
    
    document_id: str
    chunk_id: str
    revision: int


@dataclass
class ChunkRecord:
    """Represents a chunk ready for database insertion."""
    
    key: ChunkKey
    status: str
    content: str
    embedding: Embedding
    metadata: Optional[Dict[str, Any]] = None


class SupabaseClient:
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
        
        Args:
            chunk_record: ChunkRecord containing all chunk data
            
        Returns:
            Dictionary containing the inserted chunk data
        """
        data = self._prepare_chunk_data(chunk_record)
        response = self.client.table(self.table_name).insert(data).execute()
        return response.data[0]
    
    def batch_insert_chunks(self, chunk_records: List[ChunkRecord]) -> List[Dict[str, Any]]:
        """
        Batch insert multiple chunks efficiently.
        
        Args:
            chunk_records: List of ChunkRecord objects
                
        Returns:
            List of dictionaries containing the inserted chunk data
        """
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
