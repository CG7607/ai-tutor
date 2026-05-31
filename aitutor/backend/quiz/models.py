"""Pydantic models for quiz system."""
from pydantic import BaseModel


class QuizRequest(BaseModel):
    topic: str
    student_level: int = 1  # Bloom level 1-6
    history: list[dict] | None = None


class QuizSubmitRequest(BaseModel):
    question_id: str
    student_answer: str
    correct: bool


class QuizResponse(BaseModel):
    question_id: str
    question: str
    options: list[str] | None = None  # None for open-ended questions
    question_type: str  # "single_choice", "multi_choice", "short_answer", "open"
    answer: str
    explanation: str
    bloom_level: int
    adaptive_action: str  # "upgrade", "maintain", "downgrade"


class QuizSubmitResponse(BaseModel):
    acknowledged: bool
    new_level: int
    next_action: str
