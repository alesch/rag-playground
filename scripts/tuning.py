#!/usr/bin/env python3
"""
Run performance tuning experiments with configurable parameters.

Usage:
  # Quick test with 3-question questionnaire:
  python scripts/tuning.py --questionnaire test_questionnaire_short --trials 1
  
  # Full overnight run with 50-question questionnaire:
  python scripts/tuning.py --questionnaire sample_questionnaire --trials 3
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import OLLAMA_CHAT_MODEL, SQLITE_DB_PATH, OLLAMA_EMBEDDING_MODEL
from src.infrastructure.database.sqlite_client import SQLiteClient
from src.domain.models import RunConfig
from src.domain.stores.questionnaire_store import QuestionnaireStore
from src.domain.stores.run_store import RunStore
from src.domain.stores.evaluation_store import EvaluationStore
from src.experiments.run_experiments import ExperimentRunner


def create_experiment_configs():
    """Define the 7 experimental configurations to test."""
    base_config = {
        "llm_model": OLLAMA_CHAT_MODEL,
        "chunk_size": 800,
        "chunk_overlap": 100,
        "embedding_model": OLLAMA_EMBEDDING_MODEL,
        "embedding_dimensions": 1024,
    }
    
    configs = [
        RunConfig(
            id="baseline",
            name="Baseline",
            llm_temperature=0.8,
            retrieval_top_k=5,
            similarity_threshold=0.0,
            description="Baseline configuration",
            **base_config
        ),
        RunConfig(
            id="temp-0.6",
            name="Temperature 0.6",
            llm_temperature=0.6,
            retrieval_top_k=5,
            similarity_threshold=0.0,
            description="Lower temperature for more deterministic responses",
            **base_config
        ),
        RunConfig(
            id="temp-0.5",
            name="Temperature 0.5",
            llm_temperature=0.5,
            retrieval_top_k=5,
            similarity_threshold=0.0,
            description="Even lower temperature",
            **base_config
        ),
        RunConfig(
            id="threshold-0.1",
            name="Similarity Threshold 0.1",
            llm_temperature=0.8,
            retrieval_top_k=5,
            similarity_threshold=0.1,
            description="Filter low-quality chunks with 0.1 threshold",
            **base_config
        ),
        RunConfig(
            id="threshold-0.2",
            name="Similarity Threshold 0.2",
            llm_temperature=0.8,
            retrieval_top_k=5,
            similarity_threshold=0.2,
            description="Stricter filtering with 0.2 threshold",
            **base_config
        ),
        RunConfig(
            id="topk-7",
            name="Top-K 7",
            llm_temperature=0.8,
            retrieval_top_k=7,
            similarity_threshold=0.0,
            description="Retrieve 7 chunks for more context",
            **base_config
        ),
        RunConfig(
            id="topk-10",
            name="Top-K 10",
            llm_temperature=0.8,
            retrieval_top_k=10,
            similarity_threshold=0.0,
            description="Retrieve 10 chunks for maximum context",
            **base_config
        ),
    ]
    
    return configs


def setup_stores():
    """Initialize database client and stores."""
    db_client = SQLiteClient(db_path=str(SQLITE_DB_PATH))
    questionnaire_store = QuestionnaireStore(db_client)
    run_store = RunStore(db_client)
    evaluation_store = EvaluationStore(db_client)
    return db_client, questionnaire_store, run_store, evaluation_store


def list_questionnaires(questionnaire_store):
    """List all available questionnaires."""
    questionnaires = questionnaire_store.list_questionnaires()
    print("Available questionnaires:")
    for q in questionnaires:
        num_questions = len(questionnaire_store.get_questions(q.id))
        print(f"  - {q.id}: {q.name} ({num_questions} questions)")


def validate_questionnaire(questionnaire_id, questionnaire_store):
    """Validate questionnaire exists and return questions."""
    questions = questionnaire_store.get_questions(questionnaire_id)
    
    if not questions:
        print(f"Error: Questionnaire '{questionnaire_id}' not found or has no questions")
        print("\nAvailable questionnaires:")
        list_questionnaires(questionnaire_store)
        sys.exit(1)
    
    return questions


def get_ground_truth_id(questionnaire_id):
    """Determine ground truth run ID based on questionnaire."""
    if "short" in questionnaire_id:
        return "ground_truth_notebooklm_short"
    return "ground_truth_notebooklm"


def print_experiment_header(questionnaire_id, questions, ground_truth_run_id, configs, trials):
    """Print experiment parameters header."""
    total_experiments = len(configs) * trials
    
    print(f"{'='*70}")
    print(f"PERFORMANCE TUNING EXPERIMENTS")
    print(f"{'='*70}")
    print(f"Questionnaire: {questionnaire_id} ({len(questions)} questions)")
    print(f"Ground Truth: {ground_truth_run_id}")
    print(f"Configurations: {len(configs)}")
    print(f"Trials per config: {trials}")
    print(f"Total experiments: {total_experiments}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")


def print_results_summary(results, configs):
    """Print summary of experiment results."""
    print(f"\n{'='*70}")
    print(f"EXPERIMENT RESULTS SUMMARY")
    print(f"{'='*70}\n")
    
    for config_id, data in results.items():
        trials = data["trials"]
        relevancies = [t["mean_answer_relevancy"] for t in trials]
        mean_relevancy = sum(relevancies) / len(relevancies)
        
        config = next(c for c in configs if c.id == config_id)
        print(f"{config.name}:")
        print(f"  Mean Relevancy: {mean_relevancy:.4f}")
        print(f"  Trials: {[f'{r:.4f}' for r in relevancies]}")
        print()
    
    print(f"{'='*70}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Results saved to: {SQLITE_DB_PATH}")
    print(f"{'='*70}")


def main():
    """Run experiments with specified questionnaire and trials."""
    parser = argparse.ArgumentParser(description="Run performance tuning experiments")
    parser.add_argument(
        "--questionnaire",
        type=str,
        default="test_questionnaire_short",
        help="Questionnaire ID (default: test_questionnaire_short)"
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=1,
        help="Number of trials per configuration (default: 1)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available questionnaires and exit"
    )
    args = parser.parse_args()
    
    # Setup stores
    db_client, questionnaire_store, run_store, evaluation_store = setup_stores()
    
    # List questionnaires if requested
    if args.list:
        list_questionnaires(questionnaire_store)
        return
    
    # Validate questionnaire
    questions = validate_questionnaire(args.questionnaire, questionnaire_store)
    ground_truth_run_id = get_ground_truth_id(args.questionnaire)
    
    # Prepare experiments
    configs = create_experiment_configs()
    print_experiment_header(args.questionnaire, questions, ground_truth_run_id, configs, args.trials)
    
    # Create experiment runner
    runner = ExperimentRunner(
        db_client=db_client,
        questionnaire_store=questionnaire_store,
        run_store=run_store,
        evaluation_store=evaluation_store
    )
    
    # Run experiments
    results = runner.run_experiments(
        questionnaire_id=args.questionnaire,
        ground_truth_run_id=ground_truth_run_id,
        configs=configs,
        trials_per_config=args.trials
    )
    
    # Display results
    print_results_summary(results, configs)


if __name__ == "__main__":
    main()
