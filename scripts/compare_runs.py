#!/usr/bin/env python3
"""
Compare performance tuning runs from the database.
Shows configurations and metrics for all evaluation runs.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.sqlite_client import SQLiteClient
from src.config import SQLITE_DB_PATH

def main():
    db_path = str(SQLITE_DB_PATH)
    db_client = SQLiteClient(db_path)
    conn = db_client.conn
    cursor = conn.cursor()
    
    # Get all evaluation runs (exclude ground truth)
    cursor.execute("""
        SELECT 
            r.id as run_id,
            r.name,
            r.created_at,
            rc.llm_model,
            rc.llm_temperature,
            rc.retrieval_top_k,
            rc.similarity_threshold,
            rc.chunk_size,
            rc.chunk_overlap
        FROM runs r
        JOIN run_configurations rc ON r.run_configuration_id = rc.id
        WHERE r.id LIKE 'eval%'
        ORDER BY r.created_at DESC
    """)
    
    runs = cursor.fetchall()
    
    if not runs:
        print("No evaluation runs found in database.")
        return
    
    print("\n" + "=" * 140)
    print(f"{'Run ID':<25} {'Name':<30} {'Model':<12} {'Temp':<6} {'Top-K':<6} {'Thresh':<7} {'Created':<20}")
    print("=" * 140)
    
    for run in runs:
        # Get mean answer relevancy from evaluation results if available
        cursor.execute("""
            SELECT AVG(
                json_extract(meta_json, '$.answer_relevancy')
            ) as mean_relevancy
            FROM answers
            WHERE run_id = ? AND is_success = 1
            AND meta_json LIKE '%answer_relevancy%'
        """, (run['run_id'],))
        
        result = cursor.fetchone()
        mean_relevancy = result['mean_relevancy'] if result and result['mean_relevancy'] else None
        
        # Get answer count
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM answers
            WHERE run_id = ? AND is_success = 1
        """, (run['run_id'],))
        
        answer_count = cursor.fetchone()['count']
        
        print(f"{run['run_id']:<25} {run['name'][:29]:<30} {run['llm_model']:<12} "
              f"{run['llm_temperature']:<6.1f} {run['retrieval_top_k']:<6} "
              f"{run['similarity_threshold']:<7.1f} {run['created_at']:<20}")
        
        if mean_relevancy:
            print(f"  → Answers: {answer_count}, Mean Relevancy: {mean_relevancy:.4f}")
        else:
            print(f"  → Answers: {answer_count} (no evaluation metrics)")
        print()
    
    print("=" * 140)
    print(f"\nTotal evaluation runs: {len(runs)}")
    print(f"Database: {db_path}")

if __name__ == "__main__":
    main()
