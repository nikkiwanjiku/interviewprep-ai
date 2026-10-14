from io import BytesIO
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from app.database import get_db
from app.dependencies import get_current_user

from app.models.user import User
from app.models.interview import Interview
from app.models.interview_answer import InterviewAnswer


router = APIRouter(
    prefix="/report",
    tags=["Interview Report"]
)


# ==========================================================
# DOWNLOAD INTERVIEW REPORT
# GET /report/{interview_id}
# ==========================================================

@router.get("/{interview_id}")
def download_report(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # ------------------------------------------------------
    # current_user is already a User object
    # ------------------------------------------------------

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="User authentication required."
        )

    # ------------------------------------------------------
    # Find the interview belonging to this user
    # ------------------------------------------------------

    interview = (
        db.query(Interview)
        .filter(
            Interview.id == interview_id,
            Interview.user_id == current_user.id
        )
        .first()
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found."
        )

    # ------------------------------------------------------
    # Get all answers for this interview
    # ------------------------------------------------------

    answers = (
        db.query(InterviewAnswer)
        .filter(
            InterviewAnswer.interview_id == interview.id
        )
        .order_by(InterviewAnswer.id)
        .all()
    )

    # ------------------------------------------------------
    # Create PDF buffer
    # ------------------------------------------------------

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        title="Akira Prep Interview Report",
        author="Akira Prep"
    )

    styles = getSampleStyleSheet()

    story = []

    # ======================================================
    # REPORT HEADER
    # ======================================================

    story.append(
        Paragraph(
            "Akira Prep Interview Report",
            styles["Title"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    # ======================================================
    # CANDIDATE INFORMATION
    # ======================================================

    candidate_name = (
        current_user.full_name
        if current_user.full_name
        else current_user.email
    )

    category_name = (
        interview.category.name
        if interview.category
        else "N/A"
    )

    story.append(
        Paragraph(
            f"<b>Candidate:</b> "
            f"{escape(str(candidate_name))}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Email:</b> "
            f"{escape(str(current_user.email))}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Category:</b> "
            f"{escape(str(category_name))}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Difficulty:</b> "
            f"{escape(str(interview.difficulty))}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Total Questions:</b> "
            f"{interview.question_count}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Total Score:</b> "
            f"{interview.total_score or 0}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Status:</b> "
            f"{escape(str(interview.status or 'N/A'))}",
            styles["Normal"]
        )
    )

    story.append(
        Spacer(1, 20)
    )

    # ======================================================
    # ANSWERS
    # ======================================================

    if not answers:

        story.append(
            Paragraph(
                "No answers have been submitted for this interview.",
                styles["Normal"]
            )
        )

    else:

        for index, answer in enumerate(answers, start=1):

            # ------------------------------------------------
            # Question number
            # ------------------------------------------------

            story.append(
                Paragraph(
                    f"Question {index}",
                    styles["Heading2"]
                )
            )

            story.append(
                Spacer(1, 5)
            )

            # ------------------------------------------------
            # Question
            # ------------------------------------------------

            question_text = (
                answer.question.question
                if answer.question
                else "Question unavailable."
            )

            story.append(
                Paragraph(
                    f"<b>Question:</b> "
                    f"{escape(str(question_text))}",
                    styles["Normal"]
                )
            )

            story.append(
                Spacer(1, 8)
            )

            # ------------------------------------------------
            # User answer
            # ------------------------------------------------

            user_answer = (
                answer.user_answer
                if answer.user_answer
                else "No answer provided."
            )

            story.append(
                Paragraph(
                    f"<b>Your Answer:</b> "
                    f"{escape(str(user_answer))}",
                    styles["Normal"]
                )
            )

            story.append(
                Spacer(1, 8)
            )

            # ------------------------------------------------
            # Score
            # ------------------------------------------------

            story.append(
                Paragraph(
                    f"<b>Score:</b> "
                    f"{answer.score}/10",
                    styles["Normal"]
                )
            )

            story.append(
                Spacer(1, 8)
            )

            # ------------------------------------------------
            # Feedback
            # ------------------------------------------------

            feedback = (
                answer.feedback
                if answer.feedback
                else "No feedback available."
            )

            story.append(
                Paragraph(
                    f"<b>Feedback:</b> "
                    f"{escape(str(feedback))}",
                    styles["Normal"]
                )
            )

            # ------------------------------------------------
            # Strengths
            # ------------------------------------------------

            if answer.strengths:

                story.append(
                    Spacer(1, 8)
                )

                story.append(
                    Paragraph(
                        f"<b>Strengths:</b> "
                        f"{escape(str(answer.strengths))}",
                        styles["Normal"]
                    )
                )

            # ------------------------------------------------
            # Improvements
            # ------------------------------------------------

            if answer.improvements:

                story.append(
                    Spacer(1, 8)
                )

                story.append(
                    Paragraph(
                        f"<b>Areas for Improvement:</b> "
                        f"{escape(str(answer.improvements))}",
                        styles["Normal"]
                    )
                )

            # ------------------------------------------------
            # Ideal Answer
            # ------------------------------------------------

            if answer.ideal_answer:

                story.append(
                    Spacer(1, 8)
                )

                story.append(
                    Paragraph(
                        f"<b>Ideal Answer:</b> "
                        f"{escape(str(answer.ideal_answer))}",
                        styles["Normal"]
                    )
                )

            story.append(
                Spacer(1, 20)
            )

    # ======================================================
    # BUILD PDF
    # ======================================================

    doc.build(story)

    buffer.seek(0)

    # ======================================================
    # RETURN PDF
    # ======================================================

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f"attachment; filename=akira_prep_report_{interview.id}.pdf"
        }
    )