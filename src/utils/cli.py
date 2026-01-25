"""
Shared utilities for CLI scripts.
"""

from typing import Dict, Any, Tuple
from langchain_ollama import OllamaLLM
from src.config import OLLAMA_BASE_URL, SQLITE_DB_PATH
from src.database.factory import get_db_client
from src.database.base import VectorDatabaseClient
from src.orchestration.orchestrator import Orchestrator

def print_banner(title: str, config: Dict[str, Any]):
    """Print a formatted configuration banner."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    for key, value in config.items():
        print(f"{key:12}: {value}")
    print("=" * 60 + "\n")

def setup_orchestrator(model: str, temperature: float) -> Tuple[VectorDatabaseClient, Orchestrator]:
    """
    Setup the database client and orchestrator with the given model and temperature.
    
    Returns:
        Tuple of (db_client, orchestrator)
    """
    db_client = get_db_client()
    llm = OllamaLLM(base_url=OLLAMA_BASE_URL, model=model, temperature=temperature)
    orchestrator = Orchestrator(client=db_client, llm=llm)
    return db_client, orchestrator
