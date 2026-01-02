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


def test_allow_different_revisions_of_same_chunk(client):
    """Test that different revisions of the same chunk_id can coexist."""
    # Given
    document_id = "test-doc-revisions"
    chunk_id = "chunk-001"
    
    key_rev1 = ChunkKey(document_id=document_id, chunk_id=chunk_id, revision=1)
    key_rev2 = ChunkKey(document_id=document_id, chunk_id=chunk_id, revision=2)
    
    chunk_rev1 = ChunkRecord(
        key=key_rev1,
        status="active",
        content="Content for revision 1",
        embedding=generate_embedding("Content for revision 1"),
        metadata={"version": 1}
    )
    
    chunk_rev2 = ChunkRecord(
        key=key_rev2,
        status="active",
        content="Content for revision 2",
        embedding=generate_embedding("Content for revision 2"),
        metadata={"version": 2}
    )
    
    # Cleanup before test
    client.delete_chunk(key_rev1)
    client.delete_chunk(key_rev2)
    
    try:
        # When: Insert both revisions
        result1 = client.insert_chunk(chunk_rev1)
        result2 = client.insert_chunk(chunk_rev2)
        
        # Then: Both should be inserted successfully
        assert result1["document_id"] == document_id
        assert result1["chunk_id"] == chunk_id
        assert result1["revision"] == 1
        assert result1["content"] == "Content for revision 1"
        
        assert result2["document_id"] == document_id
        assert result2["chunk_id"] == chunk_id
        assert result2["revision"] == 2
        assert result2["content"] == "Content for revision 2"
    finally:
        # Cleanup after test
        client.delete_chunk(key_rev1)
        client.delete_chunk(key_rev2)


def test_mark_previous_active_revision_as_superseded(client):
    """Test that inserting a new revision marks the previous active revision as superseded."""
    # Given
    document_id = "test-doc-supersede"
    chunk_id = "chunk-001"
    
    key_rev1 = ChunkKey(document_id=document_id, chunk_id=chunk_id, revision=1)
    key_rev2 = ChunkKey(document_id=document_id, chunk_id=chunk_id, revision=2)
    
    chunk_rev1 = ChunkRecord(
        key=key_rev1,
        status="active",
        content="Content for revision 1",
        embedding=generate_embedding("Content for revision 1")
    )
    
    chunk_rev2 = ChunkRecord(
        key=key_rev2,
        status="active",
        content="Content for revision 2",
        embedding=generate_embedding("Content for revision 2")
    )
    
    # Cleanup before test
    client.delete_chunk(key_rev1)
    client.delete_chunk(key_rev2)
    
    try:
        # When: Insert revision 1 (active)
        client.insert_chunk(chunk_rev1)
        
        # And: Insert revision 2 (should automatically supersede revision 1)
        client.insert_chunk(chunk_rev2)
        
        # Then: Query all revisions for this chunk (returns dict keyed by revision)
        revisions = client.get_chunk_revisions(document_id, chunk_id)

        assert isinstance(revisions[1], ChunkRecord)
        assert revisions[1].status == "superseded", "Revision 1 should be superseded"
        assert revisions[2].status == "active", "Revision 2 should be active"
    finally:
        # Cleanup after test
        client.delete_chunk(key_rev1)
        client.delete_chunk(key_rev2)


def test_query_chunks_by_status(client):
    """Test querying and filtering chunks by status."""
    # Given
    document_id = "test-doc-status-filter"

    keys = [
        ChunkKey(document_id=document_id, chunk_id="chunk-active-1", revision=1),
        ChunkKey(document_id=document_id, chunk_id="chunk-active-2", revision=1),
        ChunkKey(document_id=document_id, chunk_id="chunk-superseded", revision=1),
    ]

    chunks = [
        ChunkRecord(
            key=keys[0],
            status="active",
            content="Active chunk 1",
            embedding=generate_embedding("Active chunk 1")
        ),
        ChunkRecord(
            key=keys[1],
            status="active",
            content="Active chunk 2",
            embedding=generate_embedding("Active chunk 2")
        ),
        ChunkRecord(
            key=keys[2],
            status="superseded",
            content="Superseded chunk",
            embedding=generate_embedding("Superseded chunk")
        ),
    ]

    # Cleanup before test
    for key in keys:
        client.delete_chunk(key)

    try:
        # When: Insert all chunks
        for chunk in chunks:
            client.insert_chunk(chunk)

        # Then: Query active chunks only
        active_chunks = client.query_chunks_by_status(document_id, "active")
        assert len(active_chunks) == 2, "Should find 2 active chunks"
        assert all(isinstance(c, ChunkRecord) for c in active_chunks)
        assert all(c.status == "active" for c in active_chunks)

        # And: Query superseded chunks only
        superseded_chunks = client.query_chunks_by_status(document_id, "superseded")
        assert len(superseded_chunks) == 1, "Should find 1 superseded chunk"
        assert isinstance(superseded_chunks[0], ChunkRecord)
        assert superseded_chunks[0].status == "superseded"
        assert superseded_chunks[0].key.chunk_id == "chunk-superseded"
    finally:
        # Cleanup after test
        for key in keys:
            client.delete_chunk(key)
