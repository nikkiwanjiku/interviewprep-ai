from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.interview import Interview
from app.models.category import Category
from app.schemas.interview_session import StartInterviewRequest

router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)


@router.post("/start")
def start_interview(
    request: StartInterviewRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == current_user["sub"])
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    category = (
        db.query(Category)
        .filter(Category.id == request.category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    interview = Interview(
        user_id=user.id,
        category_id=category.id
    )

    db.add(interview)
    db.commit()
    db.refresh(interview)

    return {
        "interview_id": interview.id,
        "message": "Interview started successfully."
    }