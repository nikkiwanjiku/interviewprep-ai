from datetime import datetime
from pydantic import BaseModel


class InterviewHistoryItem(BaseModel):
    interview_id: int
    category: str
    status: str
    total_score: int
    started_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True