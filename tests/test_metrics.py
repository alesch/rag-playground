import pytest
from src.evaluation.metrics import calculate_precision, calculate_recall, calculate_mrr, AnswerRelevancyMetric
from src.ingestion.embedder import Embedding

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

def test_calculate_recall_at_k():
    # Given
    retrieved_ids = ["doc1", "doc3", "doc2", "doc4"]
    expected_ids = ["doc1", "doc2", "doc5"]
    k = 2

    # When
    actual_recall = calculate_recall(retrieved_ids, expected_ids, k=k)

    # Then
    # Top 2 are ["doc1", "doc3"]. Only "doc1" is in expected_ids. 
    # Total expected is 3. 1/3 = 0.333...
    assert actual_recall == pytest.approx(0.333, abs=0.001)

def test_calculate_recall_all():
    # Given
    retrieved_ids = ["doc1", "doc3", "doc2", "doc4"]
    expected_ids = ["doc1", "doc2", "doc5"]

    # When
    actual_recall = calculate_recall(retrieved_ids, expected_ids)

    # Then
    # All 4 retrieved: ["doc1", "doc3", "doc2", "doc4"]
    # Expected: ["doc1", "doc2", "doc5"]
    # Found: ["doc1", "doc2"] (2 out of 3)
    assert actual_recall == pytest.approx(0.666, abs=0.001)

def test_calculate_mrr():
    # Given
    retrieved_ids = ["doc3", "doc1", "doc2"]
    expected_ids = ["doc1", "doc2"]

    # When
    actual_mrr = calculate_mrr(retrieved_ids, expected_ids)

    # Then
    # doc3 (rank 1) - Incorrect
    # doc1 (rank 2) - Correct! 1/2 = 0.5
    assert actual_mrr == 0.5

def test_calculate_mrr_first_is_correct():
    # Given
    retrieved_ids = ["doc1", "doc3", "doc2"]
    expected_ids = ["doc1", "doc2"]

    # When
    actual_mrr = calculate_mrr(retrieved_ids, expected_ids)

    # Then
    # doc1 (rank 1) - Correct! 1/1 = 1.0
    assert actual_mrr == 1.0

def test_calculate_mrr_none_correct():
    # Given
    retrieved_ids = ["doc3", "doc4", "doc5"]
    expected_ids = ["doc1", "doc2"]

    # When
    actual_mrr = calculate_mrr(retrieved_ids, expected_ids)

    # Then
    # None are relevant. MRR = 0.0
    assert actual_mrr == 0.0

def test_answer_relevancy_identity():
    # Given
    # A simple embedder that returns the same vector for everything
    fake_embedder = lambda text: Embedding(vector=[0.1] * 1024)
    metric = AnswerRelevancyMetric(embedder=fake_embedder)

    # When
    score = metric.score("text", "text")

    # Then
    # Identity should always be 1.0 (even if vector is just [0.1...])
    assert score == pytest.approx(1.0, abs=0.001)

def test_answer_relevancy_math_verification():
    # Given
    # We want to verify the cosine similarity math:
    # Vector A: [1.0, 0.0, ...]
    # Vector B: [0.8, 0.6, ...] (Magnitude 1)
    # Expected Cosine Similarity: 0.8
    
    vec_a = [0.0] * 1024
    vec_a[0] = 1.0
    vec_b = [0.0] * 1024
    vec_b[0] = 0.8
    vec_b[1] = 0.6
    
    responses = {
        "answer": Embedding(vector=vec_a),
        "truth": Embedding(vector=vec_b)
    }
    fake_embedder = lambda text: responses[text]
    
    metric = AnswerRelevancyMetric(embedder=fake_embedder)

    # When
    score = metric.score("answer", "truth")

    # Then
    assert score == pytest.approx(0.8, abs=0.001)
