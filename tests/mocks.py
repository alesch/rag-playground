"""
Mock implementations of external services for testing.
"""

from src.ingestion.embedder import Embedding


def fake_generate_embedding(text: str) -> Embedding:
    """Return deterministic fake embedding (1024 dimensions of 0.1)."""
    return Embedding(vector=[0.1] * 1024)


def fake_generate_embeddings(texts: list[str]) -> list[Embedding]:
    """Return list of deterministic fake embeddings."""
    return [fake_generate_embedding(text) for text in texts]


class MockLLM:
    """Mock LLM that returns a fixed response."""

    def __init__(self, response: str = "This is a mock answer."):
        self.response = response
        self.last_prompt = None

    def invoke(self, prompt: str) -> str:
        """Return fixed response and store the prompt for inspection."""
        self.last_prompt = prompt
        return self.response
