"""
Supabase client for database operations.

Handles connection to Supabase and operations on document_chunks table.
"""

from supabase import create_client, Client
from src.config import SUPABASE_URL, SUPABASE_KEY, CHUNKS_TABLE


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
