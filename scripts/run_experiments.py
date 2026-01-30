"""Experiment runner for performance tuning trials."""


class ExperimentRunner:
    """Orchestrates multiple experiment trials."""
    
    def __init__(self, orchestrator, questionnaire_store, run_store, evaluation_store):
        self.orchestrator = orchestrator
        self.questionnaire_store = questionnaire_store
        self.run_store = run_store
        self.evaluation_store = evaluation_store
    
    def run_experiment(self, questionnaire_id, ground_truth_run_id, config):
        """Run single experiment and return results."""
        return {
            "run_id": "fake-run-id",
            "questions_answered": 3,
            "success": True
        }
