"""
Integration tests for Supabase client.

Tests database operations for storing document chunks with embeddings.
"""

import pytest
from src.database.supabase_client import SupabaseClient
from src.ingestion.embedder import generate_embedding


@pytest.fixture(scope="module")
def client():
    """Fixture to provide a Supabase client instance."""
    return SupabaseClient()


@pytest.fixture
def cleanup_test_chunk(client):
    """Fixture to clean up test chunk before and after test."""
    document_id = "test-doc-001"
    chunk_id = "chunk-001"
    revision = 1
    
    # Cleanup before test
    client.client.table(client.table_name).delete().eq(
        "document_id", document_id
    ).eq(
        "chunk_id", chunk_id
    ).eq(
        "revision", revision
    ).execute()
    
    yield {"document_id": document_id, "chunk_id": chunk_id, "revision": revision}
    
    # Cleanup after test
    client.client.table(client.table_name).delete().eq(
        "document_id", document_id
    ).eq(
        "chunk_id", chunk_id
    ).eq(
        "revision", revision
    ).execute()


def test_initialize_connection(client):
    """Test that Supabase client initializes successfully with credentials."""
    # Then
    assert client is not None, "Client should be initialized"
    assert client.is_connected(), "Client should be connected to Supabase"


def test_insert_chunk(client, cleanup_test_chunk):
    """Test inserting a chunk with content, embedding, revision, and status."""
    # Given
    document_id = cleanup_test_chunk["document_id"]
    chunk_id = cleanup_test_chunk["chunk_id"]
    revision = cleanup_test_chunk["revision"]
    status = "active"
    content = "This is test content for the chunk."
    embedding = generate_embedding(content)
    metadata = {"source_file": "test.md", "chunk_index": 0}
    
    # When
    result = client.insert_chunk(
        document_id=document_id,
        chunk_id=chunk_id,
        revision=revision,
        status=status,
        content=content,
        embedding=embedding,
        metadata=metadata
    )
    
    # Then
    assert result is not None, "Insert should return a result"
    assert result["document_id"] == document_id
    assert result["chunk_id"] == chunk_id
    assert result["revision"] == revision
    assert result["status"] == status
    assert result["content"] == content
