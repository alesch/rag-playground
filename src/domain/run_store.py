"""Storage for runs and answers."""

from typing import Optional

from src.domain.models import Run, Answer


class RunStore:
    """Manages run and answer persistence."""

    def __init__(self):
        self._runs: dict[str, Run] = {}
        self._answers: dict[str, Answer] = {}

    def save_run(self, run: Run) -> None:
        """Save a run. Raises ValueError if ID already exists."""
        if run.id in self._runs:
            raise ValueError(f"Run '{run.id}' already exists")
        self._runs[run.id] = run

    def get_run(self, id: str) -> Optional[Run]:
        """Retrieve a run by ID."""
        return self._runs.get(id)

    def save_answer(self, answer: Answer) -> None:
        """Save an answer."""
        self._answers[answer.id] = answer

    def get_answer(self, id: str) -> Optional[Answer]:
        """Retrieve an answer by ID."""
        return self._answers.get(id)

    def get_answers_for_run(self, run_id: str) -> list[Answer]:
        """Retrieve all answers for a specific run."""
        return [a for a in self._answers.values() if a.run_id == run_id]
