"""
Document chunker for splitting markdown documents by headers.

Uses LangChain's MarkdownHeaderTextSplitter for intelligent chunking
with header context preservation and size limits.
"""

from dataclasses import dataclass
from typing import List
import hashlib
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from src.ingestion.document_loader import Document


@dataclass
class Chunk:
    """Represents a chunk of a document with header hierarchy metadata."""
    
    chunk_id: str
    content: str
    metadata: dict


def _generate_chunk_id(document_id: str, index: int, content: str) -> str:
    """
    Generate a unique, deterministic chunk ID.
    
    Args:
        document_id: ID of the source document
        index: Position of chunk in document
        content: Chunk content for uniqueness
        
    Returns:
        Unique chunk ID
    """
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    return f"{document_id}-chunk-{index}-{content_hash}"


def _create_chunk_metadata(document: Document, header_metadata: dict = None) -> dict:
    """
    Create metadata for a chunk combining document and header info.
    
    Args:
        document: Source document
        header_metadata: Optional header hierarchy metadata from LangChain
        
    Returns:
        Combined metadata dictionary
    """
    metadata = {
        "document_id": document.document_id,
        "revision": document.metadata.get("version", 1)
    }
    if header_metadata:
        metadata.update(header_metadata)
    return metadata


def _create_chunk(document: Document, index: int, content: str, header_metadata: dict = None) -> Chunk:
    """
    Create a single Chunk object with ID and metadata.
    
    Args:
        document: Source document
        index: Chunk position
        content: Chunk content
        header_metadata: Optional header hierarchy metadata
        
    Returns:
        Chunk object
    """
    chunk_id = _generate_chunk_id(document.document_id, index, content)
    metadata = _create_chunk_metadata(document, header_metadata)
    return Chunk(chunk_id=chunk_id, content=content, metadata=metadata)


def _create_sub_chunks(document: Document, content: str, start_index: int, 
                       header_metadata: dict, text_splitter) -> tuple[List[Chunk], int]:
    """
    Split oversized content into multiple sub-chunks.
    
    Args:
        document: Source document
        content: Content to split
        start_index: Starting chunk index
        header_metadata: Header hierarchy metadata
        text_splitter: Splitter for oversized content
        
    Returns:
        Tuple of (sub-chunks created, next available index)
    """
    chunks = []
    chunk_index = start_index
    
    for text in text_splitter.split_text(content):
        if text.strip():
            chunk = _create_chunk(document, chunk_index, text, header_metadata)
            chunks.append(chunk)
            chunk_index += 1
    
    return chunks, chunk_index


def _process_header_split(document: Document, doc, chunk_index: int, text_splitter) -> tuple[List[Chunk], int]:
    """
    Process a single header-based split, further splitting if needed.
    
    Args:
        document: Source document
        doc: LangChain Document from header split
        chunk_index: Current chunk index
        text_splitter: Splitter for oversized chunks
        
    Returns:
        Tuple of (chunks created, updated chunk index)
    """
    content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
    header_metadata = doc.metadata if hasattr(doc, 'metadata') else {}
    
    if not content.strip():
        return [], chunk_index
    
    # Split if too large
    if len(content) > text_splitter._chunk_size:
        return _create_sub_chunks(document, content, chunk_index, header_metadata, text_splitter)
    else:
        chunk = _create_chunk(document, chunk_index, content, header_metadata)
        return [chunk], chunk_index + 1


def _chunk_without_headers(document: Document, text_splitter) -> List[Chunk]:
    """
    Chunk a document that has no headers, using size-based splitting only.
    
    Args:
        document: Document to chunk
        text_splitter: Splitter for size-based chunking
        
    Returns:
        List of chunks
    """
    chunks = []
    for i, text in enumerate(text_splitter.split_text(document.content)):
        if text.strip():
            chunks.append(_create_chunk(document, i, text))
    return chunks


def _process_header_splits(document: Document, header_splits, text_splitter) -> List[Chunk]:
    """
    Process all header-based splits into chunks.
    
    Args:
        document: Source document
        header_splits: List of header-based splits from LangChain
        text_splitter: Splitter for oversized chunks
        
    Returns:
        List of chunks
    """
    chunks = []
    chunk_index = 0
    for doc in header_splits:
        new_chunks, chunk_index = _process_header_split(document, doc, chunk_index, text_splitter)
        chunks.extend(new_chunks)
    return chunks


def _create_splitters(max_chunk_size: int, chunk_overlap: int):
    """
    Create and configure markdown and text splitters.
    
    Args:
        max_chunk_size: Maximum characters per chunk
        chunk_overlap: Character overlap between chunks
        
    Returns:
        Tuple of (markdown_splitter, text_splitter)
    """
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("##", "Header2"), ("###", "Header3")],
        strip_headers=False
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return markdown_splitter, text_splitter


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
    markdown_splitter, text_splitter = _create_splitters(max_chunk_size, chunk_overlap)
    header_splits = markdown_splitter.split_text(document.content)
    
    if not header_splits:
        return _chunk_without_headers(document, text_splitter)
    
    return _process_header_splits(document, header_splits, text_splitter)
