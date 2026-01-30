"""Experiment runner for performance tuning trials."""

from typing import Optional
from datetime import datetime
from langchain_ollama import OllamaLLM
from src.config import OLLAMA_BASE_URL
from src.domain.models import Run, RunConfig, AnswerSuccess, AnswerFailure
from src.evaluation.evaluator import RAGEvaluator
from src.ingestion.embedder import generate_embedding
from src.generation.rag_system import RAGSystem

# Retry configuration
MAX_RETRIES = 3


def _timestamp() -> str:
    """Return current time formatted as HH:MM:SS."""
    return datetime.now().strftime("%H:%M:%S")


class ExperimentRunner:
    """Orchestrates multiple experiment trials."""
    
    def __init__(
        self, 
        db_client, 
        questionnaire_store, 
        run_store, 
        evaluation_store,
        rag_system: Optional[RAGSystem] = None
    ):
        """Initialize ExperimentRunner.
        
        Args:
            db_client: Database client for storing results
            questionnaire_store: Store for retrieving questionnaires
            run_store: Store for saving runs and answers
            evaluation_store: Store for saving evaluation reports
            rag_system: Optional pre-configured RAGSystem for testing.
                       If None, will create RAGSystem from config for each experiment.
        """
        self.db_client = db_client
        self.questionnaire_store = questionnaire_store
        self.run_store = run_store
        self.evaluation_store = evaluation_store
        self._test_rag_system = rag_system  # Only used for testing
    
    def _create_rag_system(self, config: RunConfig) -> RAGSystem:
        """Create RAGSystem from config, or return test instance if provided."""
        if self._test_rag_system:
            return self._test_rag_system
        
        llm = OllamaLLM(
            base_url=OLLAMA_BASE_URL,
            model=config.llm_model,
            temperature=config.llm_temperature
        )
        
        return RAGSystem(
            client=self.db_client,
            llm=llm,
            top_k=config.retrieval_top_k,
            similarity_threshold=config.similarity_threshold
        )
    
    def run_experiment(self, questionnaire_id, ground_truth_run_id, config):
        """Run single experiment with specific configuration.
        
        Creates a RAGSystem configured with parameters from RunConfig.
        """
        # Create RAGSystem from config (or use test instance)
        rag_system = self._create_rag_system(config)
        
        # Generate unique run ID with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run = Run(id=f"run-{config.id}-{timestamp}", config=config)
        self.run_store.save_run(run)
        
        questions = self.questionnaire_store.get_questions(questionnaire_id)
        total_questions = len(questions)
        
        for idx, question in enumerate(questions, 1):
            print(f"{_timestamp()}   Question {idx}/{total_questions}", end="", flush=True)
            
            # Retry up to MAX_RETRIES times on failure
            for attempt in range(MAX_RETRIES):
                try:
                    generated_answer = rag_system.answer(question)  # Pass full Question object
                    answer = AnswerSuccess.from_GeneratedAnswer(run.id, question, generated_answer)
                    answer.save_on(self.run_store)
                    print(" ✓")
                    break  # Success, move to next question
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:
                        # Not the last attempt, retry
                        print(f" (retry {attempt + 1})", end="", flush=True)
                        continue
                    else:
                        # Last attempt failed, save as failure
                        print(" ✗")
                        answer = AnswerFailure.from_exception(run.id, question, e)
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
    
    def run_experiments(self, questionnaire_id, ground_truth_run_id, configs, trials_per_config):
        """Run multiple experiments with multiple trials per config.
        
        Args:
            questionnaire_id: ID of questionnaire to run
            ground_truth_run_id: ID of ground truth run for evaluation
            configs: List of RunConfig objects
            trials_per_config: Number of trials to run for each config
            
        Returns:
            Dictionary keyed by config ID, each containing list of trial results
        """
        results = {}
        total_experiments = len(configs) * trials_per_config
        current_experiment = 0
        
        for config in configs:
            trials = []
            for trial_num in range(trials_per_config):
                current_experiment += 1
                print(f"\n{_timestamp()} [{current_experiment}/{total_experiments}] Running: {config.name} - Trial {trial_num + 1}")
                
                # Create unique config ID for each trial
                trial_config = RunConfig(
                    id=f"{config.id}-trial{trial_num + 1}",
                    name=f"{config.name} - Trial {trial_num + 1}",
                    llm_model=config.llm_model,
                    llm_temperature=config.llm_temperature,
                    retrieval_top_k=config.retrieval_top_k,
                    similarity_threshold=config.similarity_threshold,
                    chunk_size=config.chunk_size,
                    chunk_overlap=config.chunk_overlap,
                    embedding_model=config.embedding_model,
                    embedding_dimensions=config.embedding_dimensions,
                    description=config.description
                )
                
                trial_result = self.run_experiment(
                    questionnaire_id=questionnaire_id,
                    ground_truth_run_id=ground_truth_run_id,
                    config=trial_config
                )
                trials.append(trial_result)
                
                print(f"{_timestamp()}   ✓ {config.name} - Trial {trial_num + 1} Completed - Mean Relevancy: {trial_result['mean_answer_relevancy']:.4f}")
            
            results[config.id] = {"trials": trials}
        
        return results
