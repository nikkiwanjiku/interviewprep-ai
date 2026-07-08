from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.interview import CategoryCreate
from app.models.question import Question

router = APIRouter(
    prefix="/categories",
    tags=["Interview Categories"]
)


@router.post("/")
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):

    new_category = Category(
        name=category.name,
        description=category.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@router.get("/")
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.get("/{interview_id}/questions")
def get_interview_questions(
    interview_id: int,
    db: Session = Depends(get_db)
):

    interview = (
        db.query(Interview)
        .filter(Interview.id == interview_id)
        .first()
    )

    if not interview:
        raise HTTPException(

            status_code=404,
            detail="Interview not found."
        )

    questions = (
        db.query(Question)
        .filter(
            Question.category_id == interview.category_id
        )
        .all()
    )

    return questions