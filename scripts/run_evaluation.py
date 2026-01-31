#!/usr/bin/env python3
"""
Automated evaluation runner.
Runs a questionnaire through the RAG pipeline and compares it to ground truth.
"""

import argparse
import uuid
import sys
from typing import cast
from datetime import datetime
from pathlib import Path

# Add the project root to sys.path to allow importing from src
sys.path.append(str(Path(__file__).parent.parent))

from langchain_ollama import OllamaLLM
from src.config import (
    OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL, SQLITE_DB_PATH, OLLAMA_EMBEDDING_MODEL,
    LLM_TEMPERATURE, RETRIEVAL_TOP_K, SIMILARITY_THRESHOLD
)
from scripts.cli_utils import print_banner, setup_orchestrator
from src.infrastructure.database.sqlite_client import SQLiteClient
from src.domain.models import Run, RunConfig
from src.domain.stores.questionnaire_store import QuestionnaireStore
from src.domain.stores.run_store import RunStore
from src.application.runners.questionnaire_runner import QuestionnaireRunner
from src.rag.rag_system import RAGSystem
from src.application.evaluation.evaluator import RAGEvaluator
from src.domain.stores.evaluation_store import EvaluationStore
from src.rag.ingestion.embedder import generate_embedding

def main():
    parser = argparse.ArgumentParser(description="Automated evaluation runner.")
    parser.add_argument("--model", type=str, default=OLLAMA_CHAT_MODEL, help=f"Ollama model to use (default: {OLLAMA_CHAT_MODEL})")
    parser.add_argument("--name", type=str, help="Optional name for the run")
    parser.add_argument("--top-k", type=int, default=RETRIEVAL_TOP_K, help=f"Number of chunks to retrieve (default: {RETRIEVAL_TOP_K})")
    parser.add_argument("--questionnaire", type=str, default="sample_questionnaire", help="Questionnaire ID to evaluate (default: sample_questionnaire)")
    parser.add_argument("--temp", type=float, default=LLM_TEMPERATURE, help=f"LLM temperature (default: {LLM_TEMPERATURE}, optimized for llama3.2)")
    parser.add_argument("--threshold", type=float, default=SIMILARITY_THRESHOLD, help=f"Similarity threshold (default: {SIMILARITY_THRESHOLD}, optimized for llama3.2)")
    args = parser.parse_args()

    # 1. Setup Dependencies
    temp = args.temp
    db_client, orchestrator = setup_orchestrator(model=args.model, temperature=temp)
    # Cast to SQLiteClient for specialized stores
    sqlite_client = cast(SQLiteClient, db_client)
    
    # Create RAG system from orchestrator (bypass orchestrator wrapper)
    rag_system = orchestrator.rag_system
    
    q_store = QuestionnaireStore(sqlite_client)
    run_store = RunStore(sqlite_client)
    runner = QuestionnaireRunner(rag_system, q_store, run_store)
    
    run_id = f"eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    questionnaire_id = args.questionnaire
    
    # Determine ground truth run ID based on questionnaire
    if questionnaire_id == "test_questionnaire_short":
        gt_run_id = "ground_truth_notebooklm_short"
    else:
        gt_run_id = "ground_truth_notebooklm"
    
    run_name = args.name or f"Auto Evaluation - {args.model}"
    
    print_banner("COMPLAILA EVALUATION RUNNER", {
        "Run ID": run_id,
        "Questionnaire": questionnaire_id,
        "Model": args.model,
        "Temperature": temp,
        "Top-K": args.top_k,
        "Threshold": args.threshold,
        "Base URL": OLLAMA_BASE_URL,
        "DB Path": SQLITE_DB_PATH
    })
    
    config = RunConfig(
        id=f"config-{run_id}",
        name=f"Eval run {args.model}",
        llm_model=args.model,
        llm_temperature=temp,
        retrieval_top_k=args.top_k,
        similarity_threshold=args.threshold,
        chunk_size=800,
        chunk_overlap=100,
        embedding_model=OLLAMA_EMBEDDING_MODEL,
        embedding_dimensions=1024
    )
    
    run = Run(id=run_id, config=config, name=run_name)
    
    # 3. Execute Run
    print(f"Executing questionnaire '{questionnaire_id}'...")
    runner.run_questionnaire(questionnaire_id, run)
    
    # 4. Evaluate against Ground Truth
    print(f"Comparing results against ground truth ('{gt_run_id}')...")
    
    evaluator = RAGEvaluator(run_store=run_store, embedder=generate_embedding)
    report = evaluator.evaluate_run(run_id, gt_run_id)
    
    # Save evaluation report to database
    eval_store = EvaluationStore(sqlite_client)
    eval_store.save_report(report)
    
    # 5. Output Results
    print("\n" + "=" * 60)
    print("  EVALUATION RESULTS")
    print("=" * 60)
    print(f"Run ID: {run_id}")
    print(f"Model:  {args.model} (temp={temp}, top_k={args.top_k}, threshold={args.threshold})")
    print(f"Ground Truth: {gt_run_id}")
    print("-" * 60)
    
    # Sort results by question ID for readability
    sorted_q_ids = sorted(report.results.keys(), key=lambda x: [int(p) for p in x.split(':')[1][1:].split('.')])
    
    for q_id in sorted_q_ids:
        res = report.results[q_id]
        print(f"[{res.question_id}] Relevancy: {res.answer_relevancy:.4f}")
        
    print("-" * 60)
    print(f"OVERALL MEAN RELEVANCY: {report.overall_metrics.get('mean_answer_relevancy', 0.0):.4f}")
    print("=" * 60)
    print(f"\nReport and answers persisted to database ({SQLITE_DB_PATH})")

if __name__ == "__main__":
    main()
