"""Experiment runner for performance tuning trials."""

from langchain_ollama import OllamaLLM
from src.config import OLLAMA_BASE_URL
from src.domain.models import Run, AnswerSuccess
from src.evaluation.evaluator import RAGEvaluator
from src.ingestion.embedder import generate_embedding
from src.generation.rag_system import RAGSystem


class ExperimentRunner:
    """Orchestrates multiple experiment trials."""
    
    def __init__(self, db_client, questionnaire_store, run_store, evaluation_store):
        self.db_client = db_client
        self.questionnaire_store = questionnaire_store
        self.run_store = run_store
        self.evaluation_store = evaluation_store
    
    def run_experiment(self, questionnaire_id, ground_truth_run_id, config):
        """Run single experiment with specific configuration.
        
        Creates a RAGSystem configured with parameters from RunConfig.
        """
        # Create LLM with temperature from config
        llm = OllamaLLM(
            base_url=OLLAMA_BASE_URL,
            model=config.llm_model,
            temperature=config.llm_temperature
        )
        
        # Create RAGSystem with retrieval parameters from config
        rag_system = RAGSystem(
            client=self.db_client,
            llm=llm,
            top_k=config.retrieval_top_k,
            similarity_threshold=config.similarity_threshold
        )
        
        run = Run(id=f"run-{config.id}", config=config)
        self.run_store.save_run(run)
        
        questions = self.questionnaire_store.get_questions(questionnaire_id)
        
        for question in questions:
            generated_answer = rag_system.answer(question.text)
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
