from typing import List, Optional

def calculate_precision(retrieved_ids: List[str], expected_ids: List[str], k: Optional[int] = None) -> float:
    """
    Calculate Precision@K or Precision.
    
    Args:
        retrieved_ids: List of retrieved document IDs in order of relevance.
        expected_ids: List of ground truth relevant document IDs.
        k: The number of top results to consider. If None, considers all retrieved_ids.
        
    Returns:
        The precision score as a float between 0.0 and 1.0.
    """
    if not retrieved_ids:
        return 0.0
        
    actual_k = k if k is not None else len(retrieved_ids)
    top_k_retrieved = retrieved_ids[:actual_k]
    
    if not top_k_retrieved:
        return 0.0
        
    expected_set = set(expected_ids)
    relevant_count = sum(1 for doc_id in top_k_retrieved if doc_id in expected_set)
    
    return relevant_count / len(top_k_retrieved)
