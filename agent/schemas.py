from typing import Literal, Any
from pydantic import BaseModel, Field

class StudentProfile(BaseModel):
    student_id: str
    target_company: str
    target_role: str
    days_to_interview: int
    weak_topics: list[str]
    attempted_questions: list[dict[str, Any]]
    topic_scores: dict[str, float]
    last_updated: str  # ISO datetime string

class QuizQuestion(BaseModel):
    id: str
    topic: str
    difficulty: Literal["easy", "medium", "hard"]
    question: str
    options: list[str] | None = None
    correct_answer: str
    explanation: str

class EvaluationResult(BaseModel):
    is_correct: bool
    score: float = Field(..., ge=0.0, le=1.0)
    feedback: str
    suggested_next_topic: str | None = None
