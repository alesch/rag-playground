"""
Ingestion pipeline for processing corpus documents into Supabase.

Orchestrates: Document Loading → Chunking → Embedding → Storage
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List
from src.ingestion.document_loader import load_document
from src.ingestion.chunker import chunk_document, Chunk
from src.ingestion.embedder import generate_embeddings, Embedding
from src.database.supabase_client import SupabaseClient, ChunkKey, ChunkRecord


@dataclass
class IngestionResult:
    """Result of ingesting a document."""
    document_id: str
    chunks_stored: int


def _build_chunk_records(
    document_id: str,
    chunks: List[Chunk],
    embeddings: List[Embedding]
) -> List[ChunkRecord]:
    """
    Build ChunkRecord objects from chunks and their embeddings.

    Args:
        document_id: The document ID
        chunks: List of chunks from the chunker
        embeddings: List of embeddings matching chunks order

    Returns:
        List of ChunkRecord objects ready for database insertion
    """
    records = []
    for chunk, embedding in zip(chunks, embeddings):
        revision = chunk.metadata.get("revision", 1)
        record = ChunkRecord(
            key=ChunkKey(
                document_id=document_id,
                chunk_id=chunk.chunk_id,
                revision=revision
            ),
            status="active",
            content=chunk.content,
            embedding=embedding,
            metadata=chunk.metadata
        )
        records.append(record)
    return records


def ingest_document(document_path: Path) -> IngestionResult:
    """
    Ingest a single document through the full pipeline.

    Args:
        document_path: Path to the markdown document

    Returns:
        IngestionResult with document_id and chunks_stored count
    """
    # Load document
    document = load_document(document_path)

    # Chunk document
    chunks = chunk_document(document)

    # Generate embeddings for all chunks
    texts = [chunk.content for chunk in chunks]
    embeddings = generate_embeddings(texts)

    # Build chunk records
    chunk_records = _build_chunk_records(document.document_id, chunks, embeddings)

    # Batch insert into database
    client = SupabaseClient()
    client.batch_insert_chunks(chunk_records)

    return IngestionResult(
        document_id=document.document_id,
        chunks_stored=len(chunk_records)
    )
