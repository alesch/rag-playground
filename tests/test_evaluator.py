import pytest
from unittest.mock import MagicMock
from src.evaluation.evaluator import RAGEvaluator
from src.domain.models import AnswerSuccess, Question
from src.ingestion.embedder import Embedding

def test_evaluator_calculates_metrics_for_run():
    # Given
    run_id = "test-run"
    gt_run_id = "gt-run"
    
    # Mock stores
    run_store = MagicMock()
    
    # Test Answer
    ans1 = AnswerSuccess(
        id="a1", run_id=run_id, question_id="q1",
        answer_text="The sky is blue."
    )
    
    # Ground Truth Answer
    gt1 = AnswerSuccess(
        id="gt1", run_id=gt_run_id, question_id="q1",
        answer_text="Sky's color is blue."
    )
    
    run_store.get_answers_for_run.side_effect = lambda rid: [ans1] if rid == run_id else [gt1]
    
    # Mock embedder that returns same vector for both (perfect similarity)
    mock_embedder = MagicMock(return_value=Embedding(vector=[0.1] * 1024))
    
    evaluator = RAGEvaluator(run_store=run_store, embedder=mock_embedder)

    # When
    report = evaluator.evaluate_run(run_id, gt_run_id)

    # Then
    assert "q1" in report.results
    assert report.results["q1"].answer_relevancy == pytest.approx(1.0)
    assert report.overall_metrics["mean_answer_relevancy"] == pytest.approx(1.0)
