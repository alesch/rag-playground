"""
Integration tests for the full ingestion pipeline.

Tests end-to-end flow: Corpus → Documents → Chunks → Embeddings → Supabase
"""

import pytest
from pathlib import Path
from scripts.ingest_corpus import ingest_document
from src.database.supabase_client import SupabaseClient


@pytest.fixture(scope="module")
def client():
    """Fixture to provide a Supabase client instance."""
    return SupabaseClient()


@pytest.fixture
def corpus_path():
    """Path to the test corpus."""
    return Path(__file__).parent.parent / "data" / "corpus"


@pytest.fixture
def single_doc_path(corpus_path):
    """Path to a single test document."""
    return corpus_path / "01_technical_infrastructure.md"


class TestIngestionPipeline:
    """Integration tests for corpus ingestion."""

    def test_ingest_single_document(self, single_doc_path, client):
        """Test ingesting a single document end-to-end."""
        # Given
        document_path = single_doc_path
        document_id = "technical-infrastructure-documentation"

        # Cleanup before test
        self._cleanup_document(client, document_id)

        try:
            # When
            result = ingest_document(document_path)

            # Then
            assert result.document_id == document_id
            assert result.chunks_stored > 0

            # And: Verify chunks exist in database
            chunks = client.query_chunks_by_status(result.document_id, "active")
            assert len(chunks) == result.chunks_stored
        finally:
            # Cleanup after test
            self._cleanup_document(client, document_id)

    def _cleanup_document(self, client, document_id):
        """Remove all chunks for a document."""
        for status in ["active", "superseded"]:
            chunks = client.query_chunks_by_status(document_id, status)
            for chunk in chunks:
                client.delete_chunk(chunk.key)

    @pytest.mark.skip(reason="Not implemented yet")
    def test_ingest_full_corpus(self, corpus_path):
        """Test ingesting all documents from corpus."""
        # Given: A corpus directory with multiple documents
        # When: Ingesting the full corpus
        # Then: All documents are chunked, embedded, and stored
        pass

    @pytest.mark.skip(reason="Not implemented yet")
    def test_reingestion_supersedes_previous_revisions(self, single_doc_path):
        """Test that re-ingesting a document supersedes previous chunks."""
        # Given: A document already ingested (revision 1)
        # When: Re-ingesting the same document (revision 2)
        # Then: Previous chunks are marked as superseded
        pass

    @pytest.mark.skip(reason="Not implemented yet")
    def test_ingestion_returns_statistics(self, corpus_path):
        """Test that ingestion returns useful statistics."""
        # Given: A corpus to ingest
        # When: Running the ingestion pipeline
        # Then: Statistics include document count, chunk count, and status
        pass
