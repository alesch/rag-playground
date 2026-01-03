"""
Integration tests for the full ingestion pipeline.

Tests end-to-end flow: Corpus → Documents → Chunks → Embeddings → Supabase
"""

import pytest
from pathlib import Path
from scripts.ingest_corpus import ingest_document, ingest_corpus
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

    def test_ingest_full_corpus(self, corpus_path, client):
        """Test ingesting all documents from corpus."""
        # Given
        expected_doc_count = 4

        # Cleanup before test
        for doc_id in self._get_corpus_document_ids():
            self._cleanup_document(client, doc_id)

        try:
            # When
            result = ingest_corpus(corpus_path)

            # Then
            assert result.documents_processed == expected_doc_count
            assert result.total_chunks_stored > 0

            # And: Verify chunks exist for each document
            for doc_id in self._get_corpus_document_ids():
                chunks = client.query_chunks_by_status(doc_id, "active")
                assert len(chunks) > 0, f"No chunks found for {doc_id}"
        finally:
            # Cleanup after test
            for doc_id in self._get_corpus_document_ids():
                self._cleanup_document(client, doc_id)

    def _get_corpus_document_ids(self):
        """Return expected document IDs from corpus."""
        return [
            "technical-infrastructure-documentation",
            "soc-2-compliance-documentation",
            "iso-27001-compliance-documentation",
            "operational-procedures-policies",
        ]

    def test_reingestion_supersedes_previous_revisions(self, client, tmp_path):
        """Test that re-ingesting a document supersedes previous chunks."""
        # Given
        doc_path = tmp_path / "test_doc.md"
        doc_path.write_text("""---
version: 1
title: Test Supersede Document
---

## Section One

Content for section one.
""")
        document_id = "test-supersede-document"
        self._cleanup_document(client, document_id)

        try:
            # When: Ingest version 1
            result_v1 = ingest_document(doc_path)
            assert result_v1.chunks_stored > 0

            # And: Update document to version 2 and re-ingest
            doc_path.write_text("""---
version: 2
title: Test Supersede Document
---

## Section One

Content for section one.
""")
            result_v2 = ingest_document(doc_path)

            # Then: Version 1 chunks should be superseded
            superseded = client.query_chunks_by_status(document_id, "superseded")
            active = client.query_chunks_by_status(document_id, "active")

            assert len(superseded) > 0, "Should have superseded chunks"
            assert len(active) > 0, "Should have active chunks"
            assert all(c.key.revision == 1 for c in superseded), "Superseded should be rev 1"
            assert all(c.key.revision == 2 for c in active), "Active should be rev 2"
        finally:
            self._cleanup_document(client, document_id)

    @pytest.mark.skip(reason="Not implemented yet")
    def test_ingestion_returns_statistics(self, corpus_path):
        """Test that ingestion returns useful statistics."""
        # Given: A corpus to ingest
        # When: Running the ingestion pipeline
        # Then: Statistics include document count, chunk count, and status
        pass
