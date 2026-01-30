#!/usr/bin/env python3
"""
Calculate statistics from multiple evaluation trials.
Used for rigorous statistical testing of configuration changes.
"""

import statistics
from typing import List


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
