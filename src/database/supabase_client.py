"""
Supabase client for database operations.

Handles connection to Supabase and operations on document_chunks table.
"""

from supabase import create_client, Client
from typing import Dict, Any, Optional
from src.config import SUPABASE_URL, SUPABASE_KEY, CHUNKS_TABLE
from src.ingestion.embedder import Embedding


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
    
    def insert_chunk(
        self,
        document_id: str,
        chunk_id: str,
        revision: int,
        status: str,
        content: str,
        embedding: Embedding,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Insert a chunk with content, embedding, revision, and status.
        
        Args:
            document_id: Logical document identifier
            chunk_id: Unique chunk identifier
            revision: Document revision number
            status: Chunk status (e.g., 'active', 'superseded', 'archived')
            content: Chunk text content
            embedding: Embedding dataclass with 1024-dimensional vector
            metadata: Optional metadata dictionary
            
        Returns:
            Dictionary containing the inserted chunk data
        """
        data = {
            "document_id": document_id,
            "chunk_id": chunk_id,
            "revision": revision,
            "status": status,
            "content": content,
            "embedding": embedding.vector,
            "metadata": metadata
        }
        
        response = self.client.table(self.table_name).insert(data).execute()
        return response.data[0]
