from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    question = Column(Text, nullable=False)

    expected_answer = Column(Text, nullable=False)

    difficulty = Column(String(20), nullable=False)

    points = Column(Integer, default=10)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )

    category = relationship(
        "Category",
        back_populates="questions"
    )

    interview_answers = relationship(
        "InterviewAnswer",
        back_populates="question"
    )