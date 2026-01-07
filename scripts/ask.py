#!/usr/bin/env python3
"""
Interactive CLI for asking questions to the Complaila RAG system.

Usage:
    python scripts/ask.py                    # Interactive mode
    python scripts/ask.py "Your question"   # Single question mode
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_ollama import OllamaLLM
from src.config import OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL
from src.database.supabase_client import SupabaseClient
from src.orchestration.orchestrator import Orchestrator


def create_orchestrator() -> Orchestrator:
    """Create an Orchestrator with real dependencies."""
    client = SupabaseClient()
    llm = OllamaLLM(base_url=OLLAMA_BASE_URL, model=OLLAMA_CHAT_MODEL)
    return Orchestrator(client=client, llm=llm)


def print_answer(result):
    """Print the answer with citations."""
    print("\n" + "=" * 60)
    print("ANSWER:")
    print("=" * 60)
    print(result.answer)

    if result.citations:
        print("\n" + "-" * 60)
        print("SOURCES:")
        print("-" * 60)
        for i, citation in enumerate(result.citations, 1):
            print(f"\n[{i}] {citation.key.document_id}")
            print(f"    Chunk: {citation.key.chunk_id}")
            print(f"    Preview: {citation.content_snippet}...")
    print()


def interactive_mode(orchestrator: Orchestrator):
    """Run interactive question-answering loop."""
    print("\n" + "=" * 60)
    print("  Complaila RAG - Compliance Question Answering")
    print("=" * 60)
    print("\nType your questions below. Commands:")
    print("  'quit' or 'exit' - Exit the program")
    print("  'help' - Show sample questions")
    print()

    sample_questions = [
        "What authentication methods does finanso support?",
        "How is data encrypted in transit and at rest?",
        "Are you SOC 2 compliant?",
        "What is your disaster recovery plan?",
        "How do you handle software updates?",
    ]

    while True:
        try:
            question = input("Question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not question:
            continue

        if question.lower() in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break

        if question.lower() == 'help':
            print("\nSample questions:")
            for q in sample_questions:
                print(f"  - {q}")
            print()
            continue

        print("\nSearching and generating answer...")
        try:
            result = orchestrator.answer(question)
            print_answer(result)
        except Exception as e:
            print(f"\nError: {e}\n")


def single_question_mode(orchestrator: Orchestrator, question: str):
    """Answer a single question and exit."""
    print(f"\nQuestion: {question}")
    print("Searching and generating answer...")
    result = orchestrator.answer(question)
    print_answer(result)


def main():
    """Main entry point."""
    print("Initializing Complaila RAG system...")

    try:
        orchestrator = create_orchestrator()
    except Exception as e:
        print(f"Error initializing: {e}")
        sys.exit(1)

    if len(sys.argv) > 1:
        # Single question mode
        question = " ".join(sys.argv[1:])
        single_question_mode(orchestrator, question)
    else:
        # Interactive mode
        interactive_mode(orchestrator)


if __name__ == "__main__":
    main()
