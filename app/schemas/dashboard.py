from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_interviews: int
    completed_interviews: int
    in_progress_interviews: int
    average_score: float
    highest_score: int