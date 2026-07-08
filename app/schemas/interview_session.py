from pydantic import BaseModel


class StartInterviewRequest(BaseModel):
    category_id: int


class StartInterviewResponse(BaseModel):
    interview_id: int
    message: str

    class Config:
        from_attributes = True