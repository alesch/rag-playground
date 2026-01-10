"""
Base interface for vector database clients.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from src.ingestion.embedder import Embedding


@dataclass
class ChunkKey:
    """Represents the composite key for a chunk."""
    document_id: str
    chunk_id: str
    revision: int


@dataclass
class ChunkRecord:
    """Represents a chunk ready for database insertion."""
    key: ChunkKey
    status: str
    content: str
    embedding: Embedding
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SearchResult:
    """A chunk with its similarity score from vector search."""
    chunk: ChunkRecord
    similarity: float


class VectorDatabaseClient(ABC):
    """Abstract base class for vector database operations."""

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the client is connected to the database."""
        pass

    @abstractmethod
    def insert_chunk(self, chunk_record: ChunkRecord) -> Dict[str, Any]:
        """Insert a single chunk."""
        pass

    @abstractmethod
    def batch_insert_chunks(self, chunk_records: List[ChunkRecord]) -> List[Dict[str, Any]]:
        """Batch insert multiple chunks."""
        pass

    @abstractmethod
    def delete_chunk(self, key: ChunkKey) -> None:
        """Delete a specific chunk."""
        pass

    @abstractmethod
    def get_chunk_revisions(self, document_id: str, chunk_id: str) -> Dict[int, ChunkRecord]:
        """Get all revisions for a specific chunk."""
        pass

    @abstractmethod
    def query_chunks_by_status(self, document_id: str, status: str) -> List[ChunkRecord]:
        """Query chunks filtered by document_id and status."""
        pass

    @abstractmethod
    def search_by_embedding(
        self,
        query_embedding: Embedding,
        top_k: int = 5,
        threshold: float = 0.0,
        status: str = "active"
    ) -> List[SearchResult]:
        """Search for similar chunks by embedding."""
        pass
