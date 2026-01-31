"""Storage for questionnaires and questions."""

import re
from pathlib import Path
from typing import Optional

from src.domain.models import Questionnaire, Question
from src.infrastructure.database.sqlite_client import SQLiteClient


class QuestionnaireStore:
    """Manages questionnaire persistence."""

    def __init__(self, db_client: SQLiteClient):
        self.db_client = db_client
        self.conn = db_client.conn

    def save_questionnaire(self, questionnaire: Questionnaire) -> None:
        """Save a questionnaire. Raises ValueError if ID already exists."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO questionnaires (id, name, description, source_file, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                questionnaire.id,
                questionnaire.name,
                questionnaire.description,
                questionnaire.source_file,
                questionnaire.status
            ))
            self.conn.commit()
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(f"Questionnaire '{questionnaire.id}' already exists")
            raise

    def get_questionnaire(self, id: str) -> Optional[Questionnaire]:
        """Retrieve a questionnaire by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM questionnaires WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Questionnaire(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            source_file=row['source_file'],
            status=row['status']
        )

    def list_questionnaires(self, status: Optional[str] = None) -> list[Questionnaire]:
        """List questionnaires, optionally filtered by status."""
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * FROM questionnaires WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT * FROM questionnaires")
        
        return [
            Questionnaire(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                source_file=row['source_file'],
                status=row['status']
            )
            for row in cursor.fetchall()
        ]

    def save_questions(self, questions: list[Question]) -> None:
        """Save a batch of questions."""
        cursor = self.conn.cursor()
        for q in questions:
            cursor.execute("""
                INSERT OR REPLACE INTO questions (id, questionnaire_id, question_id, text, section, sequence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                q.id,
                q.questionnaire_id,
                q.question_id,
                q.text,
                q.section,
                q.sequence
            ))
        self.conn.commit()

    def get_questions(self, questionnaire_id: str) -> list[Question]:
        """Retrieve all questions for a questionnaire, ordered by sequence."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM questions 
            WHERE questionnaire_id = ? 
            ORDER BY sequence
        """, (questionnaire_id,))
        
        return [
            Question(
                id=row['id'],
                questionnaire_id=row['questionnaire_id'],
                question_id=row['question_id'],
                text=row['text'],
                section=row['section'],
                sequence=row['sequence']
            )
            for row in cursor.fetchall()
        ]

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
