#!/usr/bin/env python3
"""
Automated evaluation runner.
Runs a questionnaire through the RAG pipeline and compares it to ground truth.
"""

import argparse
import uuid
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to sys.path to allow importing from src
sys.path.append(str(Path(__file__).parent.parent))

from langchain_ollama import OllamaLLM
from src.config import OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL, SQLITE_DB_PATH, OLLAMA_EMBEDDING_MODEL
from src.database.sqlite_client import SQLiteClient
from src.domain.models import Run, RunConfig
from src.domain.questionnaire_store import QuestionnaireStore
from src.domain.run_store import RunStore
from src.domain.runner import QuestionnaireRunner
from src.orchestration.orchestrator import Orchestrator
from src.evaluation.evaluator import RAGEvaluator
from src.ingestion.embedder import generate_embedding

def main():
    parser = argparse.ArgumentParser(description="Automated evaluation runner.")
    parser.add_argument("--model", type=str, default=OLLAMA_CHAT_MODEL, help=f"Ollama model to use (default: {OLLAMA_CHAT_MODEL})")
    parser.add_argument("--name", type=str, help="Optional name for the run")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve (default: 5)")
    args = parser.parse_args()

    # 1. Setup Dependencies
    db_client = SQLiteClient(str(SQLITE_DB_PATH))
    temp = 0
    llm = OllamaLLM(base_url=OLLAMA_BASE_URL, model=args.model, temperature=temp)
    orchestrator = Orchestrator(client=db_client, llm=llm)
    
    q_store = QuestionnaireStore(db_client)
    run_store = RunStore(db_client)
    runner = QuestionnaireRunner(orchestrator, q_store, run_store)
    
    # 2. Configure Run
    run_id = f"eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    questionnaire_id = "sample_questionnaire"
    run_name = args.name or f"Auto Evaluation - {args.model}"
    
    print(f"Starting evaluation run: {run_id}")
    print(f"Model: {args.model}")
    
    config = RunConfig(
        id=f"config-{run_id}",
        name=f"Eval run {args.model}",
        llm_model=args.model,
        llm_temperature=temp,
        retrieval_top_k=args.top_k,
        similarity_threshold=0,
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
    gt_run_id = "ground_truth_notebooklm"
    print(f"Comparing results against ground truth ('{gt_run_id}')...")
    
    evaluator = RAGEvaluator(run_store=run_store, embedder=generate_embedding)
    report = evaluator.evaluate_run(run_id, gt_run_id)
    
    # 5. Output Results
    print("\n" + "=" * 60)
    print("  EVALUATION RESULTS")
    print("=" * 60)
    print(f"Run ID: {run_id}")
    print(f"Model:  {OLLAMA_CHAT_MODEL}")
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
