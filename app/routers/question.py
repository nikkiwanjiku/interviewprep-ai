from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.question import Question
from app.schemas.question import QuestionCreate

router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)


@router.post("/")
def create_question(
    question: QuestionCreate,
    db: Session = Depends(get_db)
):

    new_question = Question(
        question=question.question,
        expected_answer=question.expected_answer,
        difficulty=question.difficulty,
        category_id=question.category_id
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question


@router.get("/")
def get_questions(
    db: Session = Depends(get_db)
):
    return db.query(Question).all()