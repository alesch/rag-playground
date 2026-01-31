#!/usr/bin/env python3
"""
Calculate statistics from multiple evaluation trials.
Used for rigorous statistical testing of configuration changes.
"""

import sys
import os
from pathlib import Path
import statistics
import argparse
from typing import List

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infrastructure.database.sqlite_client import SQLiteClient
from src.config import SQLITE_DB_PATH


def calculate_statistics(scores: List[float]) -> dict:
    """
    Calculate statistical measures for a list of scores.
    
    Args:
        scores: List of relevancy scores
        
    Returns:
        Dictionary with mean, stdev, min, max, count
    """
    if not scores:
        return {
            'mean': 0.0,
            'stdev': 0.0,
            'min': 0.0,
            'max': 0.0,
            'count': 0
        }
    
    return {
        'mean': statistics.mean(scores),
        'stdev': statistics.stdev(scores) if len(scores) > 1 else 0.0,
        'min': min(scores),
        'max': max(scores),
        'count': len(scores)
    }


def get_trial_scores(db_client, name_pattern: str, limit: int) -> List[float]:
    """
    Fetch trial scores from database matching a name pattern.
    
    Args:
        db_client: Database client instance
        name_pattern: SQL LIKE pattern to match run names
        limit: Maximum number of trials to fetch
        
    Returns:
        List of mean relevancy scores
    """
    cursor = db_client.conn.cursor()
    
    cursor.execute('''
        SELECT er.mean_answer_relevancy 
        FROM evaluation_reports er
        JOIN runs r ON er.run_id = r.id
        WHERE r.name LIKE ?
        ORDER BY r.created_at DESC
        LIMIT ?
    ''', (name_pattern, limit))
    
    return [row[0] for row in cursor.fetchall()]


def print_statistics_report(
    baseline_scores: List[float],
    optimized_scores: List[float],
    baseline_config: str = "temp=0.8, thresh=0.0",
    optimized_config: str = "temp=0.3, thresh=0.3"
) -> None:
    """
    Print formatted statistical comparison report.
    
    Args:
        baseline_scores: Scores from baseline configuration trials
        optimized_scores: Scores from optimized configuration trials
        baseline_config: Description of baseline configuration
        optimized_config: Description of optimized configuration
    """
    baseline_stats = calculate_statistics(baseline_scores)
    optimized_stats = calculate_statistics(optimized_scores)
    
    print()
    print('=' * 70)
    print('  STATISTICAL SUMMARY')
    print('=' * 70)
    print()
    
    print(f'Baseline Configuration ({baseline_config}):')
    print(f'  Trials: {baseline_stats["count"]}')
    print(f'  Scores: {[f"{s:.4f}" for s in baseline_scores]}')
    print(f'  Mean:   {baseline_stats["mean"]:.4f}')
    print(f'  Std Dev: {baseline_stats["stdev"]:.4f}')
    print(f'  Range:  [{baseline_stats["min"]:.4f}, {baseline_stats["max"]:.4f}]')
    print()
    
    print(f'Optimized Configuration ({optimized_config}):')
    print(f'  Trials: {optimized_stats["count"]}')
    print(f'  Scores: {[f"{s:.4f}" for s in optimized_scores]}')
    print(f'  Mean:   {optimized_stats["mean"]:.4f}')
    print(f'  Std Dev: {optimized_stats["stdev"]:.4f}')
    print(f'  Range:  [{optimized_stats["min"]:.4f}, {optimized_stats["max"]:.4f}]')
    print()
    
    if baseline_stats['mean'] > 0:
        improvement = ((optimized_stats['mean'] - baseline_stats['mean']) / baseline_stats['mean']) * 100
        print(f'Improvement: {improvement:+.2f}%')
        
        # Statistical significance check (simple effect size)
        if baseline_stats['count'] >= 3 and optimized_stats['count'] >= 3:
            diff_means = abs(optimized_stats['mean'] - baseline_stats['mean'])
            pooled_stdev = (baseline_stats['stdev'] + optimized_stats['stdev']) / 2
            
            if pooled_stdev > 0:
                # Simple effect size (Cohen's d approximation)
                effect_size = diff_means / pooled_stdev
                print(f'Effect Size: {effect_size:.2f}', end=' ')
                
                if effect_size < 0.2:
                    print('(negligible)')
                elif effect_size < 0.5:
                    print('(small)')
                elif effect_size < 0.8:
                    print('(medium)')
                else:
                    print('(large)')
    
    print('=' * 70)


def main():
    """Main entry point for calculating trial statistics."""
    parser = argparse.ArgumentParser(
        description='Calculate statistics from evaluation trials'
    )
    parser.add_argument(
        '--baseline-pattern',
        default='Statistical - Baseline Trial%',
        help='SQL LIKE pattern for baseline trial names'
    )
    parser.add_argument(
        '--optimized-pattern',
        default='Statistical - Optimized Trial%',
        help='SQL LIKE pattern for optimized trial names'
    )
    parser.add_argument(
        '--num-trials',
        type=int,
        default=3,
        help='Number of most recent trials to analyze per configuration'
    )
    
    args = parser.parse_args()
    
    # Connect to database
    db = SQLiteClient(str(SQLITE_DB_PATH))
    
    # Fetch trial scores
    baseline_scores = get_trial_scores(db, args.baseline_pattern, args.num_trials)
    optimized_scores = get_trial_scores(db, args.optimized_pattern, args.num_trials)
    
    # Check if we have data
    if not baseline_scores or not optimized_scores:
        print('Error: Could not fetch trial results')
        print(f'Found {len(baseline_scores)} baseline trials and {len(optimized_scores)} optimized trials')
        sys.exit(1)
    
    # Print report
    print_statistics_report(baseline_scores, optimized_scores)


if __name__ == '__main__':
    main()
