"""
Integration tests for the full ingestion pipeline.

Tests end-to-end flow: Corpus → Documents → Chunks → Embeddings → Storage
Uses mock embeddings and mock database for fast execution.
"""

import pytest
from pathlib import Path
from scripts.ingest_corpus import ingest_document, ingest_corpus


@pytest.fixture
def corpus_path():
    """Path to the test corpus."""
    return Path(__file__).parent.parent / "data" / "corpus"


@pytest.fixture
def single_doc_path(corpus_path):
    """Path to a single test document."""
    return corpus_path / "01_technical_infrastructure.md"


@pytest.fixture
def mock_database(mock_supabase_client, monkeypatch):
    """Patch SupabaseClient in ingest_corpus to use mock."""
    monkeypatch.setattr(
        "scripts.ingest_corpus.SupabaseClient",
        lambda: mock_supabase_client
    )
    return mock_supabase_client


class TestIngestionPipeline:
    """Integration tests for corpus ingestion."""

    def test_ingest_single_document(self, single_doc_path, mock_embeddings, mock_database):
        """Test ingesting a single document end-to-end."""
        # Given
        document_path = single_doc_path
        document_id = "technical-infrastructure-documentation"

        # When
        result = ingest_document(document_path)

        # Then
        assert result.document_id == document_id
        assert result.chunks_stored > 0

        # And: Verify chunks exist in mock database
        chunks = mock_database.query_chunks_by_status(result.document_id, "active")
        assert len(chunks) == result.chunks_stored

    def test_ingest_full_corpus(self, corpus_path, mock_embeddings, mock_database):
        """Test ingesting all documents from corpus."""
        # Given
        expected_doc_count = 4
        expected_doc_ids = [
            "technical-infrastructure-documentation",
            "soc-2-compliance-documentation",
            "iso-27001-compliance-documentation",
            "operational-procedures-policies",
        ]

        # When
        result = ingest_corpus(corpus_path)

        # Then
        assert result.documents_processed == expected_doc_count
        assert result.total_chunks_stored > 0

        # And: Verify chunks exist for each document
        for doc_id in expected_doc_ids:
            chunks = mock_database.query_chunks_by_status(doc_id, "active")
            assert len(chunks) > 0, f"No chunks found for {doc_id}"

    def test_reingestion_supersedes_previous_revisions(self, tmp_path, mock_embeddings, mock_database):
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
        superseded = mock_database.query_chunks_by_status(document_id, "superseded")
        active = mock_database.query_chunks_by_status(document_id, "active")

        assert len(superseded) > 0, "Should have superseded chunks"
        assert len(active) > 0, "Should have active chunks"
        assert all(c.key.revision == 1 for c in superseded), "Superseded should be rev 1"
        assert all(c.key.revision == 2 for c in active), "Active should be rev 2"

    def test_ingestion_returns_statistics(self, corpus_path, mock_embeddings, mock_database):
        """Test that ingestion returns useful statistics."""
        # Given
        expected_doc_ids = [
            "technical-infrastructure-documentation",
            "soc-2-compliance-documentation",
            "iso-27001-compliance-documentation",
            "operational-procedures-policies",
        ]

        # When
        result = ingest_corpus(corpus_path)

        # Then: Has aggregate stats
        assert result.documents_processed == 4
        assert result.total_chunks_stored > 0

        # And: Has per-document results
        assert len(result.document_results) == 4
        for doc_result in result.document_results:
            assert doc_result.document_id in expected_doc_ids
            assert doc_result.chunks_stored > 0
