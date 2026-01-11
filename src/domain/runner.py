"""Questionnaire runner module."""

from src.domain.models import Run, Answer, AnswerSuccess, AnswerFailure, Citation, ChunkKey
from src.domain.questionnaire_store import QuestionnaireStore
from src.domain.run_store import RunStore
from src.orchestration.orchestrator import Orchestrator


class QuestionnaireRunner:
    """Executes a questionnaire against a RAG pipeline."""

    def __init__(
        self,
        orchestrator: Orchestrator,
        questionnaire_store: QuestionnaireStore,
        run_store: RunStore,
    ):
        self.orchestrator = orchestrator
        self.questionnaire_store = questionnaire_store
        self.run_store = run_store

    def run_questionnaire(self, questionnaire_id: str, run: Run) -> None:
        """Run all questions in a questionnaire and save results."""
        questions = self.questionnaire_store.get_questions(questionnaire_id)
        if not questions:
            return

        # Save the run configuration first
        self.run_store.save_run(run)

        for question in questions:
            try:
                # Generate answer
                generated = self.orchestrator.answer(question.text)
                
                # Create answer object
                answer = AnswerSuccess(
                    id=f"ans-{run.id}-{question.question_id}",
                    run_id=run.id,
                    question_id=question.id,
                    answer_text=generated.answer,
                    retrieved_chunks=[], # TODO: map retrieved chunks when available in GeneratedAnswer
                    citations=self._map_citations(generated.citations)
                )
            except Exception as e:
                # Create failure object
                answer = AnswerFailure(
                    id=f"ans-{run.id}-{question.question_id}",
                    run_id=run.id,
                    question_id=question.id,
                    error_message=str(e)
                )
            
            self.run_store.save_answer(answer)

    def _map_citations(self, citations: list[Citation]) -> list[Citation]:
        """Map generator citations to domain citations."""
        return [
            Citation(
                key=ChunkKey(
                    document_id=c.key.document_id,
                    chunk_id=c.key.chunk_id,
                    revision=c.key.revision
                ),
                content_snippet=c.content_snippet
            )
            for c in citations
        ]
