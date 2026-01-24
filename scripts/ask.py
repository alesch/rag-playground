#!/usr/bin/env python3
"""
Interactive CLI for asking questions to the Complaila RAG system.

Usage:
    python scripts/ask.py                              # Interactive mode
    python scripts/ask.py "Your question"             # Single question mode
    python scripts/ask.py questionnaire.md            # Process questionnaire file

NOTE: This script is for interactive play and quick testing.
It does NOT persist answers to the database or trigger formal evaluations.
To run a persisted evaluation, use `scripts/run_evaluation.py`.
"""

import re
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_ollama import OllamaLLM
from src.config import OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL, SQLITE_DB_PATH
from src.database.factory import get_db_client
from src.orchestration.orchestrator import Orchestrator


def create_orchestrator(model: str = OLLAMA_CHAT_MODEL) -> Orchestrator:
    """Create an Orchestrator with real dependencies."""
    client = get_db_client()
    llm = OllamaLLM(base_url=OLLAMA_BASE_URL, model=model)
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


def extract_questions(markdown_path: Path) -> list[tuple[str, str]]:
    """Extract questions from a markdown questionnaire.

    Returns list of (question_id, question_text) tuples.
    """
    content = markdown_path.read_text()

    # Match patterns like "### Q1.1: Question text?"
    pattern = r'###\s+(Q[\d.]+):\s*(.+?)(?=\n|$)'
    matches = re.findall(pattern, content)

    return [(qid, question.strip()) for qid, question in matches]


def questionnaire_mode(orchestrator: Orchestrator, questionnaire_path: Path):
    """Process all questions from a questionnaire file."""
    print(f"\nProcessing questionnaire: {questionnaire_path}")
    print("=" * 70)

    questions = extract_questions(questionnaire_path)
    print(f"Found {len(questions)} questions\n")

    for i, (qid, question) in enumerate(questions, 1):
        print(f"\n{'=' * 70}")
        print(f"[{i}/{len(questions)}] {qid}: {question}")
        print("-" * 70)

        try:
            result = orchestrator.answer(question)
            print(f"\nANSWER:\n{result.answer}")

            if result.citations:
                print(f"\nSOURCES:")
                for citation in result.citations[:2]:  # Show top 2 sources
                    print(f"  - {citation.key.document_id}")
        except Exception as e:
            print(f"\nERROR: {e}")

    print(f"\n{'=' * 70}")
    print(f"Completed {len(questions)} questions")
    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Interactive CLI for the Complaila RAG system.")
    parser.add_argument("--model", type=str, default=OLLAMA_CHAT_MODEL, help=f"Ollama model to use (default: {OLLAMA_CHAT_MODEL})")
    parser.add_argument("query", nargs="*", help="A question or a path to a markdown questionnaire file")
    args = parser.parse_args()

    print(f"Initializing Complaila RAG system with model: {args.model}...")

    try:
        orchestrator = create_orchestrator(model=args.model)
    except Exception as e:
        print(f"Error initializing: {e}")
        sys.exit(1)

    if args.query:
        # Join multiple query parts if they weren't quoted
        query_str = " ".join(args.query)
        
        # Check if the query is a path to a markdown file
        potential_path = Path(query_str)
        if query_str.endswith('.md') and potential_path.exists():
            questionnaire_mode(orchestrator, potential_path)
        else:
            # Single question mode
            single_question_mode(orchestrator, query_str)
    else:
        # Interactive mode
        interactive_mode(orchestrator)


if __name__ == "__main__":
    main()
