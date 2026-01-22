import pytest
from src.evaluation.metrics import calculate_precision

def test_calculate_precision_at_k():
    # Given
    retrieved_ids = ["doc1", "doc3", "doc2", "doc4"]
    expected_ids = ["doc1", "doc2"]
    k = 2

    # When
    actual_precision = calculate_precision(retrieved_ids, expected_ids, k=k)

    # Then
    # Top 2 are ["doc1", "doc3"]. Only "doc1" is in expected_ids. 1/2 = 0.5
    assert actual_precision == 0.5

def test_calculate_precision_all():
    # Given
    retrieved_ids = ["doc1", "doc3", "doc2", "doc4"]
    expected_ids = ["doc1", "doc2"]

    # When
    actual_precision = calculate_precision(retrieved_ids, expected_ids)

    # Then
    # All 4 are checked. "doc1" and "doc2" are in expected_ids. 2/4 = 0.5
    assert actual_precision == 0.5
