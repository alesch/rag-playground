"""Orchestrator module for RAG pipeline coordination."""

from typing import List
from src.generation.rag_system import RAGSystem, GeneratedAnswer


class Orchestrator:
    """Coordinates the RAG pipeline using LangGraph."""

    def __init__(self, client=None, llm=None, top_k=5, similarity_threshold=0.0):
        self.rag_system = RAGSystem(
            client=client,
            llm=llm,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )

    def answer(self, question: str) -> GeneratedAnswer:
        """Answer a single question using RAG."""
        return self.rag_system.answer(question)

    def process_questionnaire(self, questions: List[str]) -> List[GeneratedAnswer]:
        """Process multiple questions and return answers in order."""
        return [self.answer(q) for q in questions]
