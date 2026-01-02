"""
Integration tests for Supabase client.

Tests database operations for storing document chunks with embeddings.
"""

import pytest
from src.database.supabase_client import SupabaseClient, ChunkRecord, ChunkKey
from src.ingestion.embedder import generate_embedding


@pytest.fixture(scope="module")
def client():
    """Fixture to provide a Supabase client instance."""
    return SupabaseClient()


def test_initialize_connection(client):
    """Test that Supabase client initializes successfully with credentials."""
    # When/Then
    assert client is not None, "Client should be initialized"
    assert client.is_connected(), "Client should be connected to Supabase"


def test_insert_chunk(client):
    """Test inserting a chunk with content, embedding, revision, and status."""
    # Given
    key = ChunkKey(
        document_id="test-doc-001",
        chunk_id="chunk-001",
        revision=1
    )
    status = "active"
    content = "This is test content for the chunk."
    embedding = generate_embedding(content)
    metadata = {"source_file": "test.md", "chunk_index": 0}
    
    chunk_record = ChunkRecord(
        key=key,
        status=status,
        content=content,
        embedding=embedding,
        metadata=metadata
    )
    
    # Cleanup before test
    client.delete_chunk(key)
    
    try:
        # When
        result = client.insert_chunk(chunk_record)
        
        # Then
        assert result is not None, "Insert should return a result"
        assert result["document_id"] == key.document_id
        assert result["chunk_id"] == key.chunk_id
        assert result["revision"] == key.revision
        assert result["status"] == status
        assert result["content"] == content
    finally:
        # Cleanup after test
        client.delete_chunk(key)


def test_batch_insert_chunks(client):
    """Test batch inserting multiple chunks efficiently."""
    # Given
    keys = [
        ChunkKey(
            document_id="test-doc-batch",
            chunk_id=f"chunk-{i:03d}",
            revision=1
        )
        for i in range(3)
    ]
    
    chunk_records = [
        ChunkRecord(
            key=keys[i],
            status="active",
            content=f"This is content for chunk {i}.",
            embedding=generate_embedding(f"This is content for chunk {i}."),
            metadata={"chunk_index": i}
        )
        for i in range(3)
    ]
    
    # Cleanup before test
    for key in keys:
        client.delete_chunk(key)
    
    try:
        # When
        results = client.batch_insert_chunks(chunk_records)
        
        # Then
        assert len(results) == 3, "Should insert 3 chunks"
        for i, result in enumerate(results):
            assert result["document_id"] == "test-doc-batch"
            assert result["chunk_id"] == f"chunk-{i:03d}"
            assert result["revision"] == 1
            assert result["status"] == "active"
            assert result["content"] == f"This is content for chunk {i}."
    finally:
        # Cleanup after test
        for key in keys:
            client.delete_chunk(key)


def test_unique_constraint_on_composite_key(client):
    """Test that UNIQUE constraint is enforced on (document_id, chunk_id, revision)."""
    # Given
    key = ChunkKey(
        document_id="test-doc-unique",
        chunk_id="chunk-unique",
        revision=1
    )
    content = "Test content for uniqueness."
    chunk_record = ChunkRecord(
        key=key,
        status="active",
        content=content,
        embedding=generate_embedding(content),
        metadata={"test": "unique"}
    )
    
    # Cleanup before test
    client.delete_chunk(key)
    
    try:
        # When: Insert first chunk
        client.insert_chunk(chunk_record)
        
        # Then: Attempt to insert duplicate should raise an error
        with pytest.raises(Exception) as exc_info:
            client.insert_chunk(chunk_record)
        
        # Verify it's a unique constraint violation
        error_message = str(exc_info.value).lower()
        assert "unique" in error_message or "duplicate" in error_message, \
            f"Expected unique constraint error, got: {exc_info.value}"
    finally:
        # Cleanup after test
        client.delete_chunk(key)
