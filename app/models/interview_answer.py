from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)

    interview_id = Column(
        Integer,
        ForeignKey("interviews.id"),
        nullable=False
    )

    question_id = Column(
        Integer,
        ForeignKey("questions.id"),
        nullable=False
    )

    user_answer = Column(Text, nullable=False)

    score = Column(Integer, nullable=False)

    feedback = Column(Text)

    strengths = Column(Text)

    improvements = Column(Text)

    ideal_answer = Column(Text)

    answered_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    interview = relationship(
        "Interview",
        back_populates="answers"
    )

    question = relationship(
        "Question",
        back_populates="interview_answers"
    )