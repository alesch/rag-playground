"""
Integration tests for document loader.

Tests the loading of markdown files from the filesystem and extraction
of frontmatter metadata.
"""

import pytest
from pathlib import Path
from src.ingestion.document_loader import load_document


def test_load_single_file_extracts_frontmatter():
    """Test loading a single markdown file and extracting frontmatter fields."""
    # Given
    corpus_path = Path("data/corpus")
    test_file = corpus_path / "01_technical_infrastructure.md"
    
    # When
    document = load_document(test_file)
    
    # Then
    assert document.content is not None
    assert document.metadata["version"] == 1
    assert document.metadata["title"] == "Technical Infrastructure Documentation"
    assert "technical" in document.metadata["tags"]
    assert "---" not in document.content  # Frontmatter should be stripped from content
