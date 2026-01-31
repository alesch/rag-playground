#!/usr/bin/env python3
"""
Create a short test questionnaire by extracting a subset of questions
from the existing sample_questionnaire.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infrastructure.database.sqlite_client import SQLiteClient
from src.domain.models import Questionnaire, Question, Run, RunConfig, AnswerSuccess
from src.domain.stores.questionnaire_store import QuestionnaireStore
from src.domain.stores.run_store import RunStore
from src.config import SQLITE_DB_PATH

def main():
    db_path = str(SQLITE_DB_PATH)
    print(f"Connecting to database at {db_path}...")
    db_client = SQLiteClient(db_path)
    q_store = QuestionnaireStore(db_client)
    run_store = RunStore(db_client)
    
    # Source questionnaire
    source_q_id = "sample_questionnaire"
    target_q_id = "test_questionnaire_short"
    
    # Question IDs to extract (just the Q labels)
    question_labels = ["Q1.2", "Q3.2", "Q6.2"]
    
    print(f"\n1. Reading source questionnaire '{source_q_id}'...")
    source_questionnaire = q_store.get_questionnaire(source_q_id)
    if not source_questionnaire:
        print(f"❌ Error: Source questionnaire '{source_q_id}' not found.")
        print("   Please run: python scripts/ingest_questionnaire.py data/questionnaires/sample_questionnaire.md")
        sys.exit(1)
    
    all_questions = q_store.get_questions(source_q_id)
    print(f"   Found {len(all_questions)} questions in source.")
    
    # Extract the specific questions
    selected_questions = [q for q in all_questions if q.question_id in question_labels]
    print(f"   Selected {len(selected_questions)} questions: {[q.question_id for q in selected_questions]}")
    
    if len(selected_questions) != len(question_labels):
        print(f"❌ Error: Could not find all requested questions.")
        sys.exit(1)
    
    # 2. Create or update target questionnaire
    print(f"\n2. Creating target questionnaire '{target_q_id}'...")
    existing_target = q_store.get_questionnaire(target_q_id)
    
    if existing_target:
        print(f"   ✅ Questionnaire '{target_q_id}' already exists. Will update questions.")
    else:
        target_questionnaire = Questionnaire(
            id=target_q_id,
            name="Test Questionnaire (Short Version)",
            description="Subset of 3 questions for rapid performance tuning",
            source_file="test_questionnaire_short.md",
            status="active"
        )
        q_store.save_questionnaire(target_questionnaire)
        print(f"   ✅ Questionnaire created.")
    
    # 3. Save questions under new questionnaire
    print(f"\n3. Saving questions to target questionnaire...")
    new_questions = []
    for q in selected_questions:
        new_question = Question(
            id=f"{target_q_id}:{q.question_id}",
            questionnaire_id=target_q_id,
            question_id=q.question_id,
            text=q.text,
            section=q.section,
            sequence=q.sequence
        )
        new_questions.append(new_question)
        print(f"   {q.question_id}")
    
    q_store.save_questions(new_questions)
    print(f"   ✅ Saved {len(new_questions)} questions")
    
    # 4. Copy ground truth answers
    print(f"\n4. Copying ground truth answers...")
    source_run_id = "ground_truth_notebooklm"
    target_run_id = "ground_truth_notebooklm_short"
    
    source_run = run_store.get_run(source_run_id)
    if not source_run:
        print(f"❌ Error: Source ground truth run '{source_run_id}' not found.")
        print("   Please run: python scripts/import_ground_truth.py")
        sys.exit(1)
    
    # Create target run
    existing_target_run = run_store.get_run(target_run_id)
    if existing_target_run:
        print(f"   ⚠️  Run '{target_run_id}' already exists. Will overwrite answers.")
    else:
        print(f"   Creating ground truth run '{target_run_id}'...")
        config = RunConfig(
            id="notebooklm_config_short",
            name="NotebookLM Reference Configuration (Short)",
            llm_model="NotebookLM",
            llm_temperature=0,
            retrieval_top_k=0,
            similarity_threshold=0,
            chunk_size=0,
            chunk_overlap=0,
            embedding_model="NotebookLM",
            embedding_dimensions=0,
            description="Static reference output from NotebookLM (3 questions)"
        )
        target_run = Run(id=target_run_id, config=config, name="Ground Truth - NotebookLM (Short)")
        run_store.save_run(target_run)
    
    # Copy answers for selected questions
    copied_count = 0
    for q_label in question_labels:
        source_q_id_full = f"{source_q_id}:{q_label}"
        target_q_id_full = f"{target_q_id}:{q_label}"
        
        # Get source answer
        source_answer = run_store.get_answer_by_run_and_question(source_run_id, source_q_id_full)
        if source_answer:
            # Create target answer
            target_answer = AnswerSuccess(
                id=f"ans-{target_run_id}-{q_label}",
                run_id=target_run_id,
                question_id=target_q_id_full,
                answer_text=source_answer.answer_text
            )
            run_store.save_answer(target_answer)
            copied_count += 1
            print(f"   ✅ {q_label}: answer copied")
        else:
            print(f"   ⚠️  {q_label}: source answer not found")
    
    print(f"\n{'='*60}")
    print(f"✅ SHORT QUESTIONNAIRE SETUP COMPLETE")
    print(f"{'='*60}")
    print(f"Questionnaire ID: {target_q_id}")
    print(f"Questions: {len(selected_questions)}")
    print(f"Ground Truth Run ID: {target_run_id}")
    print(f"Answers copied: {copied_count}/{len(question_labels)}")
    print(f"\nYou can now run evaluations with:")
    print(f"  python scripts/run_evaluation_short.py")

if __name__ == "__main__":
    main()
