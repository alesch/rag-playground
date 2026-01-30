"""Experiment runner for performance tuning trials."""

from src.domain.models import Run, AnswerSuccess
from src.evaluation.evaluator import RAGEvaluator
from src.ingestion.embedder import generate_embedding


class ExperimentRunner:
    """Orchestrates multiple experiment trials."""
    
    def __init__(self, orchestrator, questionnaire_store, run_store, evaluation_store):
        self.orchestrator = orchestrator
        self.questionnaire_store = questionnaire_store
        self.run_store = run_store
        self.evaluation_store = evaluation_store
    
    def run_experiment(self, questionnaire_id, ground_truth_run_id, config):
        """Run single experiment and return results."""
        run = Run(id=f"run-{config.id}", config=config)
        self.run_store.save_run(run)
        
        questions = self.questionnaire_store.get_questions(questionnaire_id)
        
        for question in questions:
            generated_answer = self.orchestrator.answer(question.text)
            answer = AnswerSuccess.from_GeneratedAnswer(run.id, question, generated_answer)
            answer.save_on(self.run_store)
        
        evaluator = RAGEvaluator(run_store=self.run_store, embedder=generate_embedding)
        report = evaluator.evaluate_run(run.id, ground_truth_run_id)
        
        self.evaluation_store.save_report(report)
        
        return {
            "run_id": run.id,
            "questions_answered": len(questions),
            "mean_answer_relevancy": report.overall_metrics.get("mean_answer_relevancy", 0.0),
            "success": True
        }
