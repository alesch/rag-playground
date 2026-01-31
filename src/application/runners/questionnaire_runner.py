"""Questionnaire runner module."""

from src.domain.models import Run, Answer, AnswerSuccess, AnswerFailure, Citation, ChunkKey
from src.domain.stores.questionnaire_store import QuestionnaireStore
from src.domain.stores.run_store import RunStore
from src.rag.rag_system import RAGSystem


class QuestionnaireRunner:
    """Executes a questionnaire against a RAG pipeline."""

    def __init__(
        self,
        rag_system: RAGSystem,
        questionnaire_store: QuestionnaireStore,
        run_store: RunStore,
    ):
        self.rag_system = rag_system
        self.questionnaire_store = questionnaire_store
        self.run_store = run_store

    def run_questionnaire(self, questionnaire_id: str, run: Run) -> None:
        """Run all questions in a questionnaire and save results."""
        questions = self.questionnaire_store.get_questions(questionnaire_id)
        if not questions:
            return

        # Save the run configuration first
        self.run_store.save_run(run)

        total = len(questions)
        for i, question in enumerate(questions, 1):
            print(f"[{i}/{total}] Processing question: {question.id}...")
            try:
                # Generate answer using full Question object for section metadata
                generated = self.rag_system.answer(question)
                
                # Create answer object using factory
                answer = AnswerSuccess.from_GeneratedAnswer(
                    run_id=run.id,
                    question=question,
                    generated_answer=generated
                )
            except Exception as e:
                # Create failure object using factory
                answer = AnswerFailure.from_exception(
                    run_id=run.id,
                    question=question,
                    exception=e
                )
            
            self.run_store.save_answer(answer)
