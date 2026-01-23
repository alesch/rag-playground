from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable
from src.domain.run_store import RunStore
from src.domain.models import AnswerSuccess
from src.ingestion.embedder import Embedding
from src.evaluation.metrics import AnswerRelevancyMetric

@dataclass
class QuestionResult:
    """Evaluation results for a single question."""
    question_id: str
    answer_relevancy: float
    # Future metrics can be added here (precision, recall if sources exist)

@dataclass
class EvaluationReport:
    """Aggregated evaluation results for a run."""
    run_id: str
    gt_run_id: str
    results: Dict[str, QuestionResult] = field(default_factory=dict)
    overall_metrics: Dict[str, float] = field(default_factory=dict)

class RAGEvaluator:
    """Coordinates evaluation of RAG runs against ground truth."""

    def __init__(self, run_store: RunStore, embedder: Callable[[str], Embedding]):
        self.run_store = run_store
        self.relevancy_metric = AnswerRelevancyMetric(embedder=embedder)

    def evaluate_run(self, run_id: str, gt_run_id: str) -> EvaluationReport:
        """
        Evaluate all answers in a run against a ground truth run.
        """
        run_answers = {a.question_id: a for a in self.run_store.get_answers_for_run(run_id) 
                       if isinstance(a, AnswerSuccess)}
        gt_answers = {a.question_id: a for a in self.run_store.get_answers_for_run(gt_run_id)
                       if isinstance(a, AnswerSuccess)}

        results = {}
        for q_id, ans in run_answers.items():
            if q_id in gt_answers:
                gt_ans = gt_answers[q_id]
                score = self.relevancy_metric.score(ans.answer_text, gt_ans.answer_text)
                results[q_id] = QuestionResult(
                    question_id=q_id,
                    answer_relevancy=score
                )

        # Calculate overall metrics
        overall = {}
        if results:
            relevancy_scores = [r.answer_relevancy for r in results.values()]
            overall["mean_answer_relevancy"] = sum(relevancy_scores) / len(relevancy_scores)

        return EvaluationReport(
            run_id=run_id,
            gt_run_id=gt_run_id,
            results=results,
            overall_metrics=overall
        )
