"""Domain models for questionnaires and answers."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Questionnaire:
    """A compliance questionnaire."""

    id: str
    name: str
    description: Optional[str] = None
    source_file: Optional[str] = None
    status: str = "active"


@dataclass
class Question:
    """A single question within a questionnaire."""

    id: str
    questionnaire_id: str
    question_id: str
    text: str
    section: Optional[str] = None
    sequence: int = 0
