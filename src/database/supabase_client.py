"""
Supabase client for database operations.

Handles connection to Supabase and operations on document_chunks table.
"""

from supabase import create_client, Client
from src.config import SUPABASE_URL, SUPABASE_KEY


class SupabaseClient:
    """Client for Supabase database operations."""
    
    def __init__(self):
        """
        Initialize Supabase client with credentials from config.
        
        Raises:
            ValueError: If credentials are not configured
        """
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase credentials not configured")
        
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def is_connected(self) -> bool:
        """
        Check if client is connected to Supabase.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            # Simple query to verify connection
            self.client.table("document_chunks").select("id").limit(1).execute()
            return True
        except Exception:
            return False
