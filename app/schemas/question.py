from pydantic import BaseModel


class QuestionCreate(BaseModel):
    question: str
    expected_answer: str
    difficulty: str
    category_id: int


class QuestionResponse(BaseModel):
    id: int
    question: str
    expected_answer: str
    difficulty: str
    category_id: int

    class Config:
        from_attributes = True


class InterviewQuestionResponse(BaseModel):
    id: int
    question: str
    difficulty: str

    class Config:
        from_attributes = True