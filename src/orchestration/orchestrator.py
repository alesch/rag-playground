"""Orchestrator module for RAG pipeline coordination."""

from typing import List
from src.generation.generator import Generator, GeneratedAnswer


class Orchestrator:
    """Coordinates the RAG pipeline using LangGraph."""

    def __init__(self, client=None, llm=None):
        self.generator = Generator(client=client, llm=llm)

    def answer(self, question: str) -> GeneratedAnswer:
        """Answer a single question using RAG."""
        return self.generator.generate(question)

    def process_questionnaire(self, questions: List[str]) -> List[GeneratedAnswer]:
        """Process multiple questions and return answers in order."""
        return [self.answer(q) for q in questions]
