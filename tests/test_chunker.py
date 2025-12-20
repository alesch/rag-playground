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
    """Test that document does NOT split at # headers."""
    # Given
    content = """# Title
## Section 1
Content A"""
    document = Document(document_id="test", content=content, metadata={})
    
    # When
    chunks = chunk_document(document)
    
    # Then
    # Level 1 headers are preserved but don't trigger splits
    # All content stays together since ## is the split point
    assert len(chunks) == 1
    assert "# Title" in chunks[0].content
    assert "## Section 1" in chunks[0].content
    assert "Content A" in chunks[0].content


def test_level_1_header_with_multiple_level_2_sections():
    """Test that # header is included with first ## section, then splits at subsequent ##."""
    # Given
    content = """# Title
## Section 1
Content A
## Section 2
Content B"""
    document = Document(document_id="test", content=content, metadata={})
    
    # When
    chunks = chunk_document(document)
    
    # Then
    assert len(chunks) == 2
    # First chunk should have # Title and ## Section 1
    assert "# Title" in chunks[0].content
    assert "## Section 1" in chunks[0].content
    assert "Content A" in chunks[0].content
    # Second chunk should have ## Section 2
    assert "## Section 2" in chunks[1].content
    assert "Content B" in chunks[1].content


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


def test_preserve_header_hierarchy_in_metadata():
    """Test that chunks preserve parent header hierarchy in metadata."""
    # Given
    content = """## Security Controls
### Authentication
MFA required for all accounts.
### Encryption
AES-256 encryption at rest."""
    document = Document(document_id="test", content=content, metadata={})
    
    # When
    chunks = chunk_document(document)
    
    # Then
    assert len(chunks) == 2
    
    # First chunk: Authentication section
    assert "Authentication" in chunks[0].content
    assert "Header2" in chunks[0].metadata
    assert chunks[0].metadata["Header2"] == "Security Controls"
    assert "Header3" in chunks[0].metadata
    assert chunks[0].metadata["Header3"] == "Authentication"
    
    # Second chunk: Encryption section
    assert "Encryption" in chunks[1].content
    assert chunks[1].metadata["Header2"] == "Security Controls"
    assert chunks[1].metadata["Header3"] == "Encryption"


def test_respect_maximum_chunk_size():
    """Test that chunks respect the maximum size limit."""
    # Given - Create a section with very long content that exceeds max size
    long_content = "A" * 5000  # 5000 characters
    content = f"## Long Section\n{long_content}"
    document = Document(document_id="test", content=content, metadata={})
    max_size = 1000  # Set max to 1000 characters
    
    # When
    chunks = chunk_document(document, max_chunk_size=max_size)
    
    # Then
    # Should split into multiple chunks
    assert len(chunks) > 1, "Long content should be split into multiple chunks"
    
    # Each chunk should respect the max size
    for i, chunk in enumerate(chunks):
        assert len(chunk.content) <= max_size, f"Chunk {i} size {len(chunk.content)} exceeds max {max_size}"
    
    # Metadata should be preserved in all sub-chunks
    for chunk in chunks:
        assert chunk.metadata.get("Header2") == "Long Section"
