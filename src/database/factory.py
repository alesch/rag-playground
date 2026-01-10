"""
Factory for creating database clients.
"""

from src.config import DB_PROVIDER
from src.database.base import VectorDatabaseClient


def get_db_client() -> VectorDatabaseClient:
    """
    Returns an instance of the configured vector database client.
    
    Returns:
        An implementation of VectorDatabaseClient
        
    Raises:
        ValueError: If DB_PROVIDER is unknown
    """
    if DB_PROVIDER == "supabase":
        from src.database.supabase_client import SupabaseClient
        return SupabaseClient()
    elif DB_PROVIDER == "sqlite":
        from src.database.sqlite_client import SQLiteClient
        return SQLiteClient()
    else:
        raise ValueError(f"Unknown DB_PROVIDER: {DB_PROVIDER}")
