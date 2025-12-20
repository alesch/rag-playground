"""
Document chunker for splitting markdown documents by headers.

Splits documents into chunks based on markdown header structure while
preserving context through header hierarchy.
"""

import re
from dataclasses import dataclass
from typing import List
from src.ingestion.document_loader import Document


@dataclass
class Chunk:
    """Represents a chunk of a document."""
    
    content: str


def _is_header(line: str) -> bool:
    """
    Check if a line is a markdown header (## or ###).
    
    Args:
        line: Line to check
        
    Returns:
        True if line is a header at level 2 or 3
    """
    return bool(re.match(r'^#{2,3}\s+', line))


def _save_chunk(chunks: List[Chunk], current_chunk: List[str]) -> None:
    """
    Save accumulated lines as a chunk if content exists.
    
    Args:
        chunks: List to append the chunk to
        current_chunk: Lines accumulated for current chunk
    """
    chunk_text = "\n".join(current_chunk).strip()
    if chunk_text:
        chunks.append(Chunk(content=chunk_text))


def chunk_document(document: Document) -> List[Chunk]:
    """
    Split a document into chunks based on markdown headers.
    
    Args:
        document: Document to chunk
        
    Returns:
        List of Chunk objects
    """
    content = document.content
    chunks = []
    
    # Split by markdown headers (## and ###)
    # Pattern matches lines starting with ## or ###
    lines = content.split("\n")
    current_chunk = []
    
    for line in lines:
        if _is_header(line):
            _save_chunk(chunks, current_chunk)
            current_chunk = []
        
        current_chunk.append(line)
    
    # Add final chunk
    _save_chunk(chunks, current_chunk)
    
    return chunks
