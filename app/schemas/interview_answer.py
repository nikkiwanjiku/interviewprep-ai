from pydantic import BaseModel


class InterviewAnswerCreate(BaseModel):

    question_id: int

    answer: str


class InterviewAnswerResponse(BaseModel):

    score: int

    feedback: str

    strengths: list[str] = []

    improvements: list[str] = []

    ideal_answer: str = ""

    interview_completed: bool = False

    class Config:

        from_attributes = True