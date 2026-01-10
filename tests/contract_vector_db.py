"""
Contract tests for VectorDatabaseClient implementations.
"""

import pytest
from src.database.base import ChunkRecord, ChunkKey
from src.ingestion.embedder import generate_embedding, Embedding

class VectorDatabaseContract:
    """
    Base class for vector database contract tests.
    Subclasses must define a 'client' fixture.
    """

    def test_initialize_connection(self, client):
        """Test that client initializes successfully."""
        assert client is not None
        assert client.is_connected()

    def test_insert_chunk(self, client):
        """Test inserting a chunk with content, embedding, revision, and status."""
        key = ChunkKey("test-doc-001", "chunk-001", 1)
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
        
        client.delete_chunk(key)
        
        try:
            result = client.insert_chunk(chunk_record)
            
            assert result is not None
            assert result["document_id"] == key.document_id
            
            # Verify persistence
            records = client.query_chunks_by_status(key.document_id, status)
            assert len(records) == 1
            assert records[0].content == content
        finally:
            client.delete_chunk(key)

    def test_batch_insert_chunks(self, client):
        """Test batch inserting multiple chunks efficiently."""
        keys = [
            ChunkKey("test-doc-batch", f"chunk-{i:03d}", 1)
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
        
        for key in keys:
            client.delete_chunk(key)
        
        try:
            results = client.batch_insert_chunks(chunk_records)
            
            assert len(results) == 3
            records = client.query_chunks_by_status("test-doc-batch", "active")
            assert len(records) == 3
        finally:
            for key in keys:
                client.delete_chunk(key)

    def test_allow_different_revisions_of_same_chunk(self, client):
        """Test that different revisions of the same chunk_id can coexist."""
        document_id = "test-doc-revisions"
        chunk_id = "chunk-001"
        
        key_rev1 = ChunkKey(document_id, chunk_id, 1)
        key_rev2 = ChunkKey(document_id, chunk_id, 2)
        
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
        
        client.delete_chunk(key_rev1)
        client.delete_chunk(key_rev2)
        
        try:
            client.insert_chunk(chunk_rev1)
            client.insert_chunk(chunk_rev2)
            
            revisions = client.get_chunk_revisions(document_id, chunk_id)
            assert len(revisions) == 2
            assert revisions[1].content == "Content for revision 1"
            assert revisions[2].content == "Content for revision 2"
        finally:
            client.delete_chunk(key_rev1)
            client.delete_chunk(key_rev2)

    def test_mark_previous_active_revision_as_superseded(self, client):
        """Test that inserting a new active revision marks the previous active one as superseded."""
        document_id = "test-doc-supersede"
        chunk_id = "chunk-001"
        
        key_rev1 = ChunkKey(document_id, chunk_id, 1)
        key_rev2 = ChunkKey(document_id, chunk_id, 2)
        
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
        
        client.delete_chunk(key_rev1)
        client.delete_chunk(key_rev2)
        
        try:
            client.insert_chunk(chunk_rev1)
            client.insert_chunk(chunk_rev2)
            
            revisions = client.get_chunk_revisions(document_id, chunk_id)
            assert revisions[1].status == "superseded"
            assert revisions[2].status == "active"
        finally:
            client.delete_chunk(key_rev1)
            client.delete_chunk(key_rev2)

    def test_vector_search(self, client):
        """Test vector similarity search."""
        # Use simple distinct vectors
        vec_a = [0.0] * 1024; vec_a[0] = 1.0
        vec_b = [0.0] * 1024; vec_b[1] = 1.0
        
        records = [
            ChunkRecord(
                key=ChunkKey("search-doc", "c1", 1),
                status="active",
                content="Chunk A",
                embedding=Embedding(vec_a)
            ),
            ChunkRecord(
                key=ChunkKey("search-doc", "c2", 1),
                status="active",
                content="Chunk B",
                embedding=Embedding(vec_b)
            )
        ]
        
        for r in records:
            client.delete_chunk(r.key)
            
        try:
            client.batch_insert_chunks(records)
            
            # Search for A (should match Chunk A)
            results = client.search_by_embedding(Embedding(vec_a), top_k=1)
            
            assert len(results) > 0
            assert results[0].chunk.content == "Chunk A"
            assert results[0].similarity > 0.9
        finally:
            for r in records:
                client.delete_chunk(r.key)