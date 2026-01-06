"""
Retriever module for similarity search.

Finds relevant document chunks for a given query using vector similarity.
"""

from typing import List, Optional
from src.database.supabase_client import SupabaseClient, SearchResult
from src.ingestion.embedder import generate_embedding


class Retriever:
    """Retrieves relevant document chunks using vector similarity search."""

    def __init__(self, client: Optional[SupabaseClient] = None):
        """
        Initialize the retriever.

        Args:
            client: SupabaseClient instance. Creates one if not provided.
        """
        self.client = client or SupabaseClient()

    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[SearchResult]:
        """
        Search for chunks similar to the query text.

        Args:
            query: Natural language query
            top_k: Maximum number of results to return
            threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            List of SearchResult objects, sorted by similarity descending
        """
        embedding = generate_embedding(query)
        return self.client.search_by_embedding(
            query_embedding=embedding,
            top_k=top_k,
            threshold=threshold
        )
