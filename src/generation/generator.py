"""
Generator module for answer generation.

Uses retrieved chunks and LLM to generate answers with citations.
"""

from dataclasses import dataclass
from typing import List, Optional
from src.database.supabase_client import SupabaseClient, SearchResult, ChunkKey
from src.retrieval.retriever import Retriever


@dataclass
class Citation:
    """Reference to a source chunk."""
    key: ChunkKey
    content_snippet: str


@dataclass
class GeneratedAnswer:
    """Answer with citations."""
    answer: str
    citations: List[Citation]


class Generator:
    """Generates answers using RAG (Retrieval-Augmented Generation)."""

    def __init__(
        self,
        client: Optional[SupabaseClient] = None,
        llm=None
    ):
        """
        Initialize the generator.

        Args:
            client: SupabaseClient for database access
            llm: LLM instance for answer generation
        """
        self.retriever = Retriever(client=client)
        self.llm = llm

    def generate(self, query: str, top_k: int = 5) -> GeneratedAnswer:
        """
        Generate an answer for the query using RAG.

        Args:
            query: The question to answer
            top_k: Number of chunks to retrieve

        Returns:
            GeneratedAnswer with answer text and citations
        """
        results = self.retriever.search(query, top_k=top_k)

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
