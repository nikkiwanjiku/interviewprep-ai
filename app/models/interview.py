from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )

    difficulty = Column(String, nullable=False)

    question_count = Column(Integer, nullable=False)

    status = Column(
        String(20),
        default="IN_PROGRESS"
    )

    total_score = Column(
        Integer,
        default=0
    )

    started_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    user = relationship(
    "User",
    back_populates="interviews"
)

    category = relationship(
        "Category",
        back_populates="interviews"
    )

    answers = relationship(
        "InterviewAnswer",
        back_populates="interview",
        cascade="all, delete"
    )
    questions = relationship(
    "InterviewQuestion",
    back_populates="interview",
    cascade="all, delete-orphan"
)