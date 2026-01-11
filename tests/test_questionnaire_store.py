"""Tests for QuestionnaireStore - manages questionnaire and question persistence."""

from pathlib import Path

import pytest

from src.domain.models import Questionnaire, Question
from src.domain.questionnaire_store import QuestionnaireStore
from src.database.sqlite_client import SQLiteClient


@pytest.fixture
def store():
    """Provide a QuestionnaireStore with an in-memory database."""
    db_client = SQLiteClient(db_path=":memory:")
    return QuestionnaireStore(db_client=db_client)


class TestQuestionnaireStore:
    """Test suite for QuestionnaireStore."""

    def test_save_and_retrieve_questionnaire_by_id(self, store):
        """Save a questionnaire and retrieve it by ID."""
        # Given
        questionnaire = Questionnaire(
            id="ikea-42",
            name="Ikea",
            description="Vendor compliance pre-sales",
            source_file="data/questionnaires/ikea.md",
        )

        # When
        store.save_questionnaire(questionnaire)
        retrieved = store.get_questionnaire("ikea-42")

        # Then
        assert retrieved is not None
        assert retrieved.id == "ikea-42"
        assert retrieved.name == "Ikea"
        assert retrieved.description == "Vendor compliance pre-sales"
        assert retrieved.source_file == "data/questionnaires/ikea.md"
        assert retrieved.status == "active"

    def test_save_batch_of_questions_with_sequence(self, store):
        """Save multiple questions maintaining their sequence order."""
        # Given
        questionnaire = Questionnaire(
            id="ikea-42",
            name="Ikea",
        )
        store.save_questionnaire(questionnaire)

        questions = [
            Question(
                id="ikea-42:Q1.1",
                questionnaire_id="ikea-42",
                question_id="Q1.1",
                text="Do you have SOC 2 certification?",
                section="Security Certifications",
                sequence=1,
            ),
            Question(
                id="ikea-42:Q1.2",
                questionnaire_id="ikea-42",
                question_id="Q1.2",
                text="When was your last security audit?",
                section="Security Certifications",
                sequence=2,
            ),
            Question(
                id="ikea-42:Q2.1",
                questionnaire_id="ikea-42",
                question_id="Q2.1",
                text="What cloud provider do you use?",
                section="Technical Infrastructure",
                sequence=3,
            ),
        ]

        # When
        store.save_questions(questions)
        retrieved = store.get_questions("ikea-42")

        # Then
        assert len(retrieved) == 3
        assert retrieved[0].question_id == "Q1.1"
        assert retrieved[0].sequence == 1
        assert retrieved[1].question_id == "Q1.2"
        assert retrieved[2].question_id == "Q2.1"
        assert retrieved[2].section == "Technical Infrastructure"

    def test_import_from_markdown_file(self, store, tmp_path):
        """Import questionnaire and questions from a markdown file."""
        # Given
        md_content = """# Ikea Vendor Assessment

## Section 1: Security

### Q1.1: Do you have SOC 2 certification?

### Q1.2: When was your last security audit?

## Section 2: Infrastructure

### Q2.1: What cloud provider do you use?
"""
        md_file = tmp_path / "ikea.md"
        md_file.write_text(md_content)

        # When
        questionnaire, questions = store.import_from_markdown(md_file)

        # Then
        assert questionnaire.id == "ikea"
        assert questionnaire.name == "Ikea Vendor Assessment"
        assert questionnaire.source_file == str(md_file)

        assert len(questions) == 3
        assert questions[0].question_id == "Q1.1"
        assert questions[0].text == "Do you have SOC 2 certification?"
        assert questions[0].section == "Section 1: Security"
        assert questions[1].question_id == "Q1.2"
        assert questions[2].question_id == "Q2.1"
        assert questions[2].section == "Section 2: Infrastructure"

    def test_list_questionnaires_filtered_by_status(self, store):
        """List questionnaires filtered by status."""
        # Given
        store.save_questionnaire(Questionnaire(id="ikea-42", name="Ikea", status="active"))
        store.save_questionnaire(Questionnaire(id="volvo-01", name="Volvo", status="active"))
        store.save_questionnaire(Questionnaire(id="old-one", name="Old", status="archived"))

        # When
        active = store.list_questionnaires(status="active")
        archived = store.list_questionnaires(status="archived")
        all_questionnaires = store.list_questionnaires()

        # Then
        assert len(active) == 2
        assert {q.id for q in active} == {"ikea-42", "volvo-01"}

        assert len(archived) == 1
        assert archived[0].id == "old-one"

        assert len(all_questionnaires) == 3

    def test_save_duplicate_questionnaire_raises_error(self, store):
        """Saving a questionnaire with existing ID raises error (insert-only)."""
        # Given
        original = Questionnaire(
            id="ikea",
            name="Ikea from Sweden",
        )
        store.save_questionnaire(original)

        duplicate = Questionnaire(
            id="ikea",
            name="Ikea from Norway",
        )

        # When / Then
        with pytest.raises(ValueError, match="already exists"):
            store.save_questionnaire(duplicate)
