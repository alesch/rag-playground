"""Domain models for questionnaires and answers."""

from dataclasses import dataclass, field
from typing import Optional, List, Any


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

    @staticmethod
    def from_generated(generated_citation: Any) -> "Citation":
        """Map a single generator citation to a domain citation."""
        return Citation(
            key=ChunkKey(
                document_id=generated_citation.key.document_id,
                chunk_id=generated_citation.key.chunk_id,
                revision=generated_citation.key.revision
            ),
            content_snippet=generated_citation.content_snippet
        )


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
class RunConfig:
    """Configuration parameters for a run (immutable)."""
    id: str
    name: str
    llm_model: str
    llm_temperature: float
    retrieval_top_k: int
    similarity_threshold: float
    chunk_size: int
    chunk_overlap: int
    embedding_model: str
    embedding_dimensions: int
    description: Optional[str] = None


@dataclass
class Run:
    """A set of answers generated with a specific configuration."""

    id: str
    config: RunConfig
    status: str = "active"
    name: Optional[str] = None  # Optional override or derivative name


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
    """Base class for an answer outcome."""
    id: str
    run_id: str
    question_id: str


@dataclass
class AnswerSuccess(Answer):
    """A successful answer generated for a question."""

    answer_text: str
    retrieved_chunks: List[RetrievedChunk] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    query_embedding: Optional[List[float]] = None
    generation_time_ms: Optional[int] = None

    @staticmethod
    def from_GeneratedAnswer(run_id: str, question: Question, generated_answer: Any) -> "AnswerSuccess":
        """Factory method to create AnswerSuccess from a GeneratedAnswer."""
        return AnswerSuccess(
            id=f"ans-{run_id}-{question.question_id}",
            run_id=run_id,
            question_id=question.id,
            answer_text=generated_answer.answer,
            retrieved_chunks=[],  # TODO: map retrieved chunks when available in GeneratedAnswer
            citations=[Citation.from_generated(c) for c in generated_answer.citations]
        )


@dataclass
class AnswerFailure(Answer):
    """A failed answer attempt."""
    error_message: str

    @staticmethod
    def from_exception(run_id: str, question: Question, exception: Exception) -> "AnswerFailure":
        """Factory method to create AnswerFailure from an Exception."""
        return AnswerFailure(
            id=f"ans-{run_id}-{question.question_id}",
            run_id=run_id,
            question_id=question.id,
            error_message=str(exception)
        )
