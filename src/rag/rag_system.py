"""
RAGSystem module for answer generation.

Uses retrieved chunks and LLM to generate answers with citations.
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from src.infrastructure.database.base import VectorDatabaseClient, SearchResult
from src.domain.models import Citation, Question
from src.rag.retriever import Retriever


@dataclass
class GeneratedAnswer:
    """Answer with citations."""
    answer: str
    citations: List[Citation]


class RAGSystem:
    """RAG system encapsulating vector DB, embeddings, and LLM."""
    
    def __init__(
        self,
        client: Optional[VectorDatabaseClient] = None,
        llm=None,
        top_k: int = 5,
        similarity_threshold: float = 0.0
    ):
        """
        Initialize the RAG system.
        
        Args:
            client: VectorDatabaseClient for database access
            llm: LLM instance for answer generation
            top_k: Number of chunks to retrieve
            similarity_threshold: Minimum similarity score for retrieval
        """
        self.retriever = Retriever(client=client)
        self.llm = llm
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

    def answer(self, question: Union[Question, str]) -> GeneratedAnswer:
        """
        Generate an answer for the question using RAG.
        
        Args:
            question: Question object (preferred) or query string (legacy)
            
        Returns:
            GeneratedAnswer with answer text and citations
        """
        # Extract query text and optional section context
        if isinstance(question, Question):
            query = question.text
            # Enhance query with section if available
            if question.section:
                query = f"{question.section}: {question.text}"
        else:
            # Legacy: accept plain string
            query = question
        
        results = self.retriever.search(query, top_k=self.top_k, threshold=self.similarity_threshold)

        if not results:
            return GeneratedAnswer(
                answer="I cannot find this information in the documentation.",
                citations=[]
            )

        prompt = self._build_prompt(query, results)
        response = self.llm.invoke(prompt)
        citations = self._extract_citations(results)

        return GeneratedAnswer(answer=response, citations=citations)

    def _build_prompt(self, query: str, results: List[SearchResult]) -> str:
        """Build the prompt with context from retrieved chunks."""
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[{i}] {result.chunk.content}")

        context = "\n\n".join(context_parts)

        return f"""You are a compliance assistant. Answer the question using ONLY the provided context.
If the answer cannot be found in the context, say "I cannot find this information in the documentation."

Context:
{context}

Question: {query}

Answer:"""

    def _extract_citations(self, results: List[SearchResult]) -> List[Citation]:
        """Extract citations from search results."""
        return [
            Citation(
                key=result.chunk.key,
                content_snippet=result.chunk.content[:100]
            )
            for result in results
        ]
