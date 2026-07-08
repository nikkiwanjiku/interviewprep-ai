from fastapi import FastAPI

from app.database import Base, engine
from app.models.user import User
from app.models.category import Category
from app.models.question import Question
from app.models.interview import Interview
from app.models.interview_answer import InterviewAnswer
from app.routers.interview_session import router as interview_session_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.interview import router as interview_router
from app.routers.question import router as question_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="InterviewPrep AI",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(interview_router)
app.include_router(interview_session_router)
app.include_router(question_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to InterviewPrep AI "
    }