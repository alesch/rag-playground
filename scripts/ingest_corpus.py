"""
Ingestion pipeline for processing corpus documents into Supabase.

Orchestrates: Document Loading → Chunking → Embedding → Storage
"""

import sys
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag.ingestion.document_loader import load_document, load_corpus as load_corpus_documents, Document
from src.rag.ingestion.chunker import chunk_document, Chunk
from src.rag.ingestion.embedder import generate_embeddings, Embedding
from src.infrastructure.database.factory import get_db_client
from src.infrastructure.database.base import VectorDatabaseClient, ChunkKey, ChunkRecord


@dataclass
class IngestionResult:
    """Result of ingesting a document."""
    document_id: str
    chunks_stored: int


@dataclass
class CorpusIngestionResult:
    """Result of ingesting a full corpus."""
    documents_processed: int
    total_chunks_stored: int
    document_results: List[IngestionResult]


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


def _process_document(document: Document, client: VectorDatabaseClient) -> int:
    """
    Process a single document: chunk, embed, and store.

    Args:
        document: Document to process
        client: Vector database client for storage

    Returns:
        Number of chunks stored
    """
    chunks = chunk_document(document)
    texts = [chunk.content for chunk in chunks]
    embeddings = generate_embeddings(texts)
    chunk_records = _build_chunk_records(document.document_id, chunks, embeddings)
    client.batch_insert_chunks(chunk_records)
    return len(chunk_records)


def ingest_document(document_path: Path, client: VectorDatabaseClient = None) -> IngestionResult:
    """
    Ingest a single document through the full pipeline.

    Args:
        document_path: Path to the markdown document
        client: Optional database client. If None, creates one from config.

    Returns:
        IngestionResult with document_id and chunks_stored count
    """
    document = load_document(document_path)
    if client is None:
        client = get_db_client()
    chunks_stored = _process_document(document, client)

    return IngestionResult(
        document_id=document.document_id,
        chunks_stored=chunks_stored
    )


def ingest_corpus(corpus_path: Path, client: VectorDatabaseClient = None) -> CorpusIngestionResult:
    """
    Ingest all documents from a corpus directory.

    Args:
        corpus_path: Path to the corpus directory
        client: Optional database client. If None, creates one from config.

    Returns:
        CorpusIngestionResult with documents_processed, total_chunks_stored,
        and per-document results
    """
    documents = load_corpus_documents(corpus_path)
    if client is None:
        client = get_db_client()

    document_results = []
    total_chunks_stored = 0
    for document in documents:
        chunks_stored = _process_document(document, client)
        total_chunks_stored += chunks_stored
        document_results.append(IngestionResult(
            document_id=document.document_id,
            chunks_stored=chunks_stored
        ))

    return CorpusIngestionResult(
        documents_processed=len(documents),
        total_chunks_stored=total_chunks_stored,
        document_results=document_results
    )


def main():
    """Main entry point for corpus ingestion."""
    from src.config import CORPUS_PATH
    
    print(f"Starting corpus ingestion from {CORPUS_PATH}...")
    try:
        result = ingest_corpus(CORPUS_PATH)
        print(f"\n✅ Ingestion completed!")
        print(f"   Documents processed: {result.documents_processed}")
        print(f"   Total chunks stored: {result.total_chunks_stored}")
        print("\nPer-document breakdown:")
        for doc in result.document_results:
            print(f"   - {doc.document_id}: {doc.chunks_stored} chunks")
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
