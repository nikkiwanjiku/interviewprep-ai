from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.interview import Interview
from app.models.interview_question import InterviewQuestion
from app.models.question import Question
from app.models.interview_answer import InterviewAnswer
from app.models.user import User

from app.schemas.interview_session import StartInterviewRequest
from app.schemas.interview_answer import (
    InterviewAnswerCreate,
    InterviewAnswerResponse
)

from app.dependencies import get_current_user


router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)


# ==========================================================
# START INTERVIEW
# POST /interview/start
# ==========================================================

@router.post("/start")
def start_interview(
    request: StartInterviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
        # ------------------------------------------------------
    # Validate question count
    # ------------------------------------------------------

    if request.question_count <= 0:
        raise HTTPException(
            status_code=400,
            detail="Question count must be greater than 0."
        )
        # ------------------------------------------------------
    # Check for an existing active interview
    # ------------------------------------------------------

    active_interview = (
        db.query(Interview)
        .filter(
            Interview.user_id == current_user.id,
            Interview.status == "IN_PROGRESS"
        )
        .first()
    )

    if active_interview:
        raise HTTPException(
            status_code=400,
            detail="You already have an interview in progress. Complete it before starting a new one."
        )
    # ------------------------------------------------------
    # Find questions
    # ------------------------------------------------------

    questions = (
    db.query(Question)
    .filter(
        Question.category_id == request.category_id,
        Question.difficulty.ilike(request.difficulty)
    )
    .limit(request.question_count)
    .all()
)

    # ------------------------------------------------------
    # Make sure enough questions exist
    # ------------------------------------------------------

    if len(questions) < request.question_count:
        raise HTTPException(
            status_code=400,
            detail="Not enough questions available for the selected difficulty."
        )

    # ------------------------------------------------------
    # Create interview
    # ------------------------------------------------------

    interview = Interview(
        user_id=current_user.id,
        category_id=request.category_id,
        difficulty=request.difficulty,
        question_count=request.question_count,
        status="IN_PROGRESS",
        total_score=0
    )

    db.add(interview)
    db.commit()
    db.refresh(interview)

    # ------------------------------------------------------
    # Attach questions with an explicit order
    # ------------------------------------------------------

    for index, question in enumerate(questions, start=1):

        interview_question = InterviewQuestion(
            interview_id=interview.id,
            question_id=question.id,
            question_order=index
        )

        db.add(interview_question)

    db.commit()

    # ------------------------------------------------------
    # Return interview ID
    # ------------------------------------------------------

    return {
        "interview_id": interview.id,
        "message": "Interview started successfully."
    }


# ==========================================================
# GET INTERVIEW QUESTIONS
# GET /interview/{interview_id}/questions
# ==========================================================

@router.get("/{interview_id}/questions")
def get_interview_questions(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ------------------------------------------------------
    # Find interview owned by current user
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
    # Get questions in interview order
    # ------------------------------------------------------

    interview_questions = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.interview_id == interview_id
        )
        .order_by(
            InterviewQuestion.question_order.asc()
        )
        .all()
    )

    # ------------------------------------------------------
    # Build response
    # ------------------------------------------------------

    return [
        {
            "id": iq.question.id,
            "question": iq.question.question,
            "expected_answer": iq.question.expected_answer,
            "points": iq.question.points,
            "category_id": iq.question.category_id,
            "difficulty": iq.question.difficulty,
            "question_order": iq.question_order,
            "created_at": iq.question.created_at
        }
        for iq in interview_questions
    ]


# ==========================================================
# SUBMIT ANSWER
# POST /interview/{interview_id}/answer
# ==========================================================

@router.post(
    "/{interview_id}/answer",
    response_model=InterviewAnswerResponse
)
def submit_answer(
    interview_id: int,
    answer_data: InterviewAnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ------------------------------------------------------
    # Find interview
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
    # Make sure interview is still active
    # ------------------------------------------------------

    if interview.status != "IN_PROGRESS":

        raise HTTPException(
            status_code=400,
            detail="This interview is no longer active."
        )

    # ------------------------------------------------------
    # Make sure question belongs to this interview
    # ------------------------------------------------------

    interview_question = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.interview_id == interview_id,
            InterviewQuestion.question_id == answer_data.question_id
        )
        .first()
    )

    if not interview_question:

        raise HTTPException(
            status_code=400,
            detail="This question does not belong to the selected interview."
        )

    # ------------------------------------------------------
    # Prevent duplicate answers
    # ------------------------------------------------------

    existing_answer = (
        db.query(InterviewAnswer)
        .filter(
            InterviewAnswer.interview_id == interview_id,
            InterviewAnswer.question_id == answer_data.question_id
        )
        .first()
    )

    if existing_answer:

        raise HTTPException(
            status_code=400,
            detail="This question has already been answered."
        )

    # ------------------------------------------------------
    # Validate answer
    # ------------------------------------------------------

    user_answer = answer_data.answer.strip()

    if not user_answer:

        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty."
        )

    # ------------------------------------------------------
    # Get question
    # ------------------------------------------------------

    question = (
        db.query(Question)
        .filter(
            Question.id == answer_data.question_id
        )
        .first()
    )

    if not question:

        raise HTTPException(
            status_code=404,
            detail="Question not found."
        )

    # ------------------------------------------------------
    # Temporary scoring logic
    #
    # This is intentionally simple for now.
    # Later we can replace this with AI evaluation.
    # ------------------------------------------------------

    answer_words = set(
        word.lower().strip(".,!?")
        for word in user_answer.split()
    )

    expected_words = set(
        word.lower().strip(".,!?")
        for word in question.expected_answer.split()
    )

    matching_words = answer_words.intersection(expected_words)

    if len(user_answer.split()) < 5:

        score = 2

        feedback = (
            "Your answer is too brief. "
            "Try explaining your reasoning and provide more detail."
        )

        strengths = "You attempted to answer the question."

        improvements = (
            "Add more explanation, relevant concepts, "
            "and an example where appropriate."
        )

    else:

        match_ratio = (
            len(matching_words) / len(expected_words)
            if expected_words
            else 0
        )

        if match_ratio >= 0.35:
            score = 10
            feedback = (
                "Good answer. You covered several important "
                "points related to the question."
            )

        elif match_ratio >= 0.20:
            score = 7
            feedback = (
                "Good start. Your answer covers some relevant "
                "ideas but could be more complete."
            )

        else:
            score = 5
            feedback = (
                "Your answer addresses the question, "
                "but it needs more relevant technical detail."
            )

        strengths = (
            "Your answer contains relevant concepts "
            "and demonstrates an attempt to explain your understanding."
        )

        improvements = (
            "Include the key concepts from the question "
            "and support your explanation with a clear example."
        )

    # ------------------------------------------------------
    # Create answer record
    # ------------------------------------------------------

    new_answer = InterviewAnswer(
        interview_id=interview_id,
        question_id=answer_data.question_id,
        user_answer=user_answer,
        score=score,
        feedback=feedback,
        strengths=strengths,
        improvements=improvements,
        ideal_answer=question.expected_answer
    )

    db.add(new_answer)

    # ------------------------------------------------------
    # Update interview score
    # ------------------------------------------------------

    interview.total_score = (
        interview.total_score or 0
    ) + score

    # ------------------------------------------------------
    # Check whether interview is complete
    # ------------------------------------------------------

    answered_count = (
        db.query(InterviewAnswer)
        .filter(
            InterviewAnswer.interview_id == interview_id
        )
        .count()
    )

    # +1 because the current answer has not been committed yet
    answered_count += 1

    if answered_count >= interview.question_count:

        interview.status = "COMPLETED"

        from datetime import datetime

        interview.completed_at = datetime.utcnow()

    # ------------------------------------------------------
    # Save everything
    # ------------------------------------------------------

    db.commit()
    db.refresh(new_answer)

    # ------------------------------------------------------
    # Return feedback
    # ------------------------------------------------------

    return {
        "score": score,
        "feedback": feedback,
        "strengths": [strengths],
        "improvements": [improvements],
        "ideal_answer": question.expected_answer,
        "interview_completed": interview.status == "COMPLETED"
    }

    # ==========================================================
# ==========================================================
# DASHBOARD SUMMARY
# GET /interview/dashboard
# ==========================================================

@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == current_user.id)
        .all()
    )

    completed = [
        interview for interview in interviews
        if str(interview.status or "").upper() == "COMPLETED"
    ]

    in_progress = [
        interview for interview in interviews
        if str(interview.status or "").upper() == "IN_PROGRESS"
    ]

    percentages = []
    for interview in completed:
        question_count = int(interview.question_count or 0)
        if question_count <= 0:
            continue

        possible_score = question_count * 10
        score = float(interview.total_score or 0)
        percentage = (score / possible_score) * 100
        percentages.append(min(100.0, max(0.0, percentage)))

    average_score = (
        round(sum(percentages) / len(percentages), 1)
        if percentages else 0.0
    )
    highest_score = round(max(percentages)) if percentages else 0

    return {
        "total_interviews": len(interviews),
        "completed_interviews": len(completed),
        "in_progress_interviews": len(in_progress),
        "average_score": average_score,
        "highest_score": highest_score,
    }


# INTERVIEW HISTORY
# GET /interview/history
# ==========================================================

@router.get("/history")
def get_interview_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    interviews = (
        db.query(Interview)
        .filter(
            Interview.user_id == current_user.id
        )
        .order_by(
            Interview.id.desc()
        )
        .all()
    )

    return [
        {
            "id": interview.id,
            "category": interview.category.name,
            "difficulty": interview.difficulty,
            "question_count": interview.question_count,
            "total_score": interview.total_score,
            "status": interview.status,
            "completed_at": interview.completed_at
        }
        for interview in interviews
    ]
# ==========================================================
# INTERVIEW RESULT
# GET /interview/{interview_id}/result
# ==========================================================

@router.get("/{interview_id}/result")
def get_interview_result(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ------------------------------------------------------
    # Find interview owned by current user
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
    # Get all answers
    # ------------------------------------------------------

    answers = (
        db.query(InterviewAnswer)
        .filter(
            InterviewAnswer.interview_id == interview_id
        )
        .order_by(
            InterviewAnswer.id.asc()
        )
        .all()
    )

    # ------------------------------------------------------
    # Build result
    # ------------------------------------------------------

    return {
        "interview_id": interview.id,
        "category": interview.category.name,
        "difficulty": interview.difficulty,
        "question_count": interview.question_count,
        "total_score": interview.total_score,
        "status": interview.status,
        "completed_at": interview.completed_at,

        "answers": [
            {
                "question_id": answer.question_id,
                "question": answer.question.question,
                "your_answer": answer.user_answer,
                "score": answer.score,
                "feedback": answer.feedback,
                "strengths": (
                    [answer.strengths]
                    if answer.strengths
                    else []
                ),
                "improvements": (
                    [answer.improvements]
                    if answer.improvements
                    else []
                ),
                "ideal_answer": answer.ideal_answer
            }
            for answer in answers
        ]
    }
# ==========================================================
# GET INTERVIEW DETAILS
# GET /interview/{interview_id}
# ==========================================================

@router.get("/{interview_id}")
def get_interview_details(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ------------------------------------------------------
    # Find interview owned by current user
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
        .order_by(
            InterviewAnswer.answered_at.asc()
        )
        .all()
    )

    # ------------------------------------------------------
    # Build response
    # ------------------------------------------------------

    return {
        "id": interview.id,
        "category": interview.category.name,
        "difficulty": interview.difficulty,
        "question_count": interview.question_count,
        "total_score": interview.total_score,
        "status": interview.status,
        "started_at": interview.started_at,
        "completed_at": interview.completed_at,

        "answers": [
            {
                "question_id": answer.question_id,
                "question": answer.question.question,
                "user_answer": answer.user_answer,
                "score": answer.score,
                "feedback": answer.feedback,
                "strengths": answer.strengths,
                "improvements": answer.improvements,
                "ideal_answer": answer.ideal_answer,
                "answered_at": answer.answered_at
            }
            for answer in answers
        ]
    }
