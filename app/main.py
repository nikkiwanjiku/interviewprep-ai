from fastapi import FastAPI

from app.database import Base, engine
from app.models.user import User
from app.models.category import Category
from app.models.question import Question
from app.models.interview import Interview
from app.models.interview_answer import InterviewAnswer
from app.models.interview_question import InterviewQuestion
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.question import router as question_router
from app.routers.interview_session import router as interview_session_router
from app.routers.categories import router as categories_router
from app.routers.report import router as report_router
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="InterviewPrep AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(question_router)
app.include_router(interview_session_router)
app.include_router(report_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to InterviewPrep AI"
    }