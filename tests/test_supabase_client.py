"""
Integration tests for Supabase client.

Tests database operations for storing document chunks with embeddings.
"""

import pytest
from src.database.supabase_client import SupabaseClient


def test_initialize_connection():
    """Test that Supabase client initializes successfully with credentials."""
    # When
    client = SupabaseClient()
    
    # Then
    assert client is not None, "Client should be initialized"
    assert client.is_connected(), "Client should be connected to Supabase"
