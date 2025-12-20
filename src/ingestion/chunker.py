"""
Document chunker for splitting markdown documents by headers.

Uses LangChain's MarkdownHeaderTextSplitter for intelligent chunking
with header context preservation and size limits.
"""

from dataclasses import dataclass
from typing import List
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from src.ingestion.document_loader import Document


@dataclass
class Chunk:
    """Represents a chunk of a document with header hierarchy metadata."""
    
    content: str
    metadata: dict


def chunk_document(
    document: Document,
    max_chunk_size: int = 4000,
    chunk_overlap: int = 200
) -> List[Chunk]:
    """
    Split a document into chunks using LangChain's markdown-aware splitter.
    
    Two-phase approach:
    1. Split by markdown headers (## and ###) to preserve structure
    2. Further split oversized chunks to respect max_chunk_size
    
    Args:
        document: Document to chunk
        max_chunk_size: Maximum characters per chunk (~1000 tokens)
        chunk_overlap: Character overlap between chunks for context
        
    Returns:
        List of Chunk objects
    """
    # Phase 1: Split by headers
    headers_to_split_on = [
        ("##", "Header2"),
        ("###", "Header3"),
    ]
    
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False  # Keep headers in content for context
    )
    
    # Phase 2: Enforce size limits
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    # Apply both splitters
    header_splits = markdown_splitter.split_text(document.content)
    
    # If no header splits (document without headers), split by size only
    if not header_splits:
        final_splits = text_splitter.split_text(document.content)
        return [Chunk(content=text, metadata={}) for text in final_splits if text.strip()]
    
    # Further split large chunks
    chunks = []
    for doc in header_splits:
        # LangChain returns Document objects with page_content and metadata
        content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
        metadata = doc.metadata if hasattr(doc, 'metadata') else {}
        
        # Split if too large
        if len(content) > max_chunk_size:
            sub_chunks = text_splitter.split_text(content)
            # Preserve metadata in sub-chunks
            chunks.extend([Chunk(content=text, metadata=metadata) for text in sub_chunks if text.strip()])
        else:
            if content.strip():
                chunks.append(Chunk(content=content, metadata=metadata))
    
    return chunks
