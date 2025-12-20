"""
Integration tests for document chunker.

Tests the chunking of documents by markdown headers with context preservation.
"""

import pytest
from pathlib import Path
from src.ingestion.document_loader import load_document, Document
from src.ingestion.chunker import chunk_document


def test_split_document_into_chunks():
    """Test that document is split into multiple chunks."""
    # Given
    corpus_path = Path("data/corpus")
    test_file = corpus_path / "01_technical_infrastructure.md"
    document = load_document(test_file)
    
    # When
    chunks = chunk_document(document)
    
    # Then
    assert len(chunks) > 1, "Document should be split into multiple chunks"
    assert all(chunk.content for chunk in chunks), "All chunks should have content"


def test_split_at_level_2_headers():
    """Test that document splits at ## headers."""
    # Given
    content = """## Section 1
Content A
## Section 2
Content B"""
    document = Document(document_id="test", content=content, metadata={})
    
    # When
    chunks = chunk_document(document)
    
    # Then
    assert len(chunks) == 2
    assert "## Section 1" in chunks[0].content
    assert "Content A" in chunks[0].content
    assert "## Section 2" in chunks[1].content
    assert "Content B" in chunks[1].content


def test_split_at_level_3_headers():
    """Test that document splits at ### headers."""
    # Given
    content = """### Subsection 1
Content A
### Subsection 2
Content B"""
    document = Document(document_id="test", content=content, metadata={})
    
    # When
    chunks = chunk_document(document)
    
    # Then
    assert len(chunks) == 2
    assert "### Subsection 1" in chunks[0].content
    assert "### Subsection 2" in chunks[1].content


def test_no_split_at_level_1_headers():
    """Test that document does NOT split at # headers but does split at ##."""
    # Given
    content = """# Title
## Section 1
Content A"""
    document = Document(document_id="test", content=content, metadata={})
    
    # When
    chunks = chunk_document(document)
    
    # Then
    # Level 1 header stays in first chunk (no split), but ## does trigger split
    assert len(chunks) == 2
    assert chunks[0].content == "# Title"
    assert "## Section 1" in chunks[1].content
    assert "Content A" in chunks[1].content


def test_consecutive_headers():
    """Test handling of consecutive headers with no content between."""
    # Given
    content = """## Section 1
## Section 2
Content B"""
    document = Document(document_id="test", content=content, metadata={})
    
    # When
    chunks = chunk_document(document)
    
    # Then
    assert len(chunks) == 2
    assert chunks[0].content == "## Section 1"
    assert "## Section 2" in chunks[1].content
    assert "Content B" in chunks[1].content


def test_empty_document():
    """Test handling of empty document."""
    # Given
    content = ""
    document = Document(document_id="test", content=content, metadata={})
    
    # When
    chunks = chunk_document(document)
    
    # Then
    assert len(chunks) == 0, "Empty document should produce no chunks"


def test_document_without_headers():
    """Test handling of document with no headers."""
    # Given
    content = """Just some content
without any headers
at all."""
    document = Document(document_id="test", content=content, metadata={})
    
    # When
    chunks = chunk_document(document)
    
    # Then
    assert len(chunks) == 1
    assert chunks[0].content == content
