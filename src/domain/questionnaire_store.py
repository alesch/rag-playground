"""Storage for questionnaires and questions."""

import re
from pathlib import Path
from typing import Optional

from src.domain.models import Questionnaire, Question


class QuestionnaireStore:
    """Manages questionnaire persistence."""

    def __init__(self):
        self._questionnaires: dict[str, Questionnaire] = {}
        self._questions: dict[str, list[Question]] = {}

    def save_questionnaire(self, questionnaire: Questionnaire) -> None:
        """Save a questionnaire. Raises ValueError if ID already exists."""
        if questionnaire.id in self._questionnaires:
            raise ValueError(f"Questionnaire '{questionnaire.id}' already exists")
        self._questionnaires[questionnaire.id] = questionnaire

    def get_questionnaire(self, id: str) -> Optional[Questionnaire]:
        """Retrieve a questionnaire by ID."""
        return self._questionnaires.get(id)

    def list_questionnaires(self, status: Optional[str] = None) -> list[Questionnaire]:
        """List questionnaires, optionally filtered by status."""
        questionnaires = list(self._questionnaires.values())
        if status is not None:
            questionnaires = [q for q in questionnaires if q.status == status]
        return questionnaires

    def save_questions(self, questions: list[Question]) -> None:
        """Save a batch of questions."""
        for q in questions:
            self._questions.setdefault(q.questionnaire_id, []).append(q)

    def get_questions(self, questionnaire_id: str) -> list[Question]:
        """Retrieve all questions for a questionnaire, ordered by sequence."""
        questions = self._questions.get(questionnaire_id, [])
        return sorted(questions, key=lambda q: q.sequence)

    def import_from_markdown(self, path: Path) -> tuple[Questionnaire, list[Question]]:
        """Import questionnaire and questions from a markdown file."""
        content = path.read_text()
        questionnaire_id = path.stem

        questionnaire = Questionnaire(
            id=questionnaire_id,
            name=self._extract_title(content, path.stem),
            source_file=str(path),
        )

        questions = self._extract_questions(content, questionnaire_id)

        self.save_questionnaire(questionnaire)
        self.save_questions(questions)

        return questionnaire, questions

    def _extract_title(self, content: str, fallback: str) -> str:
        """Extract title from first H1 heading."""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else fallback

    def _extract_questions(self, content: str, questionnaire_id: str) -> list[Question]:
        """Extract questions from markdown content."""
        questions = []
        current_section = None
        sequence = 0

        for line in content.split('\n'):
            # Track current section (## Section X: Name)
            section_match = re.match(r'^##\s+(.+)$', line)
            if section_match:
                current_section = section_match.group(1).strip()
                continue

            # Extract questions (### Q1.1: Question text?)
            question_match = re.match(r'^###\s+(Q[\d.]+):\s*(.+?)$', line)
            if question_match:
                sequence += 1
                question_id = question_match.group(1)
                text = question_match.group(2).strip()

                questions.append(Question(
                    id=f"{questionnaire_id}:{question_id}",
                    questionnaire_id=questionnaire_id,
                    question_id=question_id,
                    text=text,
                    section=current_section,
                    sequence=sequence,
                ))

        return questions
