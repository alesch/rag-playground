"""Orchestrator module for RAG pipeline coordination.

NOTE: Currently a thin wrapper around RAGSystem for backward compatibility.
Future LangGraph integration will add:
- State management for multi-step workflows
- Conditional routing (e.g., retry logic, web search fallback)
- Human-in-the-loop capabilities
"""

from typing import List
from src.rag.rag_system import RAGSystem, GeneratedAnswer


class Orchestrator:
    """Coordinates the RAG pipeline.
    
    Currently delegates to RAGSystem. Will be enhanced with LangGraph
    for stateful workflows and conditional routing in Phase 6 Component 2.
    """

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
