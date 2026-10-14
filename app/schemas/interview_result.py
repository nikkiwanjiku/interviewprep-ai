from datetime import datetime
from pydantic import BaseModel


class AnswerResult(BaseModel):
    question: str
    user_answer: str
    score: int
    feedback: str

    strengths: list[str]

    improvements: list[str]

    ideal_answer: str

    class Config:
        from_attributes = True


class InterviewResult(BaseModel):
    interview_id: int

    status: str

    total_score: int

    percentage: float

    overall_feedback: str

    overall_strengths: list[str]

    overall_improvements: list[str]

    recommendation: str

    started_at: datetime

    completed_at: datetime | None

    answers: list[AnswerResult]

    class Config:
        from_attributes = True