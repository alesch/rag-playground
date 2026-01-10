"""Domain models for questionnaires and answers."""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class ChunkKey:
    """Composite key identifying a chunk."""

    document_id: str
    chunk_id: str
    revision: int


@dataclass
class Citation:
    """Reference to a source chunk."""

    key: ChunkKey
    content_snippet: str


@dataclass
class Questionnaire:
    """A compliance questionnaire."""

    id: str
    name: str
    description: Optional[str] = None
    source_file: Optional[str] = None
    status: str = "active"


@dataclass
class Question:
    """A single question within a questionnaire."""

    id: str
    questionnaire_id: str
    question_id: str
    text: str
    section: Optional[str] = None
    sequence: int = 0


@dataclass
class Run:
    """A set of answers generated with a specific configuration."""

    id: str
    llm_model: str
    llm_temperature: float
    retrieval_top_k: int
    similarity_threshold: float
    chunk_size: int
    chunk_overlap: int
    embedding_model: str
    embedding_dimensions: int
    name: Optional[str] = None
    description: Optional[str] = None
    status: str = "active"


@dataclass
class RetrievedChunk:
    """Snapshot of a retrieved chunk with its similarity score."""

    document_id: str
    chunk_id: str
    revision: int
    content: str
    similarity_score: float
    rank: int


@dataclass
class Answer:
    """An answer generated for a question within a run."""

    id: str
    run_id: str
    question_id: str
    answer_text: str
    retrieved_chunks: List[RetrievedChunk] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    query_embedding: Optional[List[float]] = None
    generation_time_ms: Optional[int] = None
