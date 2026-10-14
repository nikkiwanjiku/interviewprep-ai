import json
import os

import google.generativeai as genai
from dotenv import load_dotenv


# ==========================================================
# GEMINI CONFIGURATION
# ==========================================================

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


# ==========================================================
# GENERATE INTERVIEW QUESTIONS
# ==========================================================

def generate_questions(
    category_name: str,
    category_description: str,
    difficulty: str,
    question_count: int
):

    prompt = f"""
You are an expert technical interviewer
creating questions for a software engineering
interview preparation platform.

Category:
{category_name}

Category description:
{category_description}

Difficulty:
{difficulty}

Generate exactly {question_count} interview questions.

The questions should be realistic questions that
a software engineering candidate could actually
encounter in a technical interview.

Return ONLY valid JSON.

The response must be a JSON array in this exact format:

[
    {{
        "question": "",
        "expected_answer": "",
        "difficulty": "{difficulty}",
        "points": 10
    }}
]

Rules:

- Generate exactly {question_count} questions.
- Every question must belong to the requested category.
- Do not repeat questions.
- Questions should test understanding rather than memorization.
- expected_answer should explain the important points
  a strong candidate should mention.
- Keep expected_answer concise but useful.
- difficulty must be "{difficulty}".
- points must be 10.
- Return ONLY JSON.
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    # Remove Markdown code fences if Gemini adds them
    if text.startswith("```"):

        text = text.replace(
            "```json",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        text = text.strip()

    return json.loads(text)


# ==========================================================
# EVALUATE INDIVIDUAL ANSWER
# ==========================================================

def evaluate_answer(
    expected_answer: str,
    user_answer: str
):

    prompt = f"""
You are an expert technical interviewer.

Expected answer:

{expected_answer}

Candidate answer:

{user_answer}

Evaluate the candidate's answer.

Return ONLY valid JSON.

{{
    "score": 0,
    "feedback": "",
    "strengths": [],
    "improvements": [],
    "ideal_answer": ""
}}

Rules:

- score must be between 0 and 10.
- strengths must be a list.
- improvements must be a list.
- ideal_answer should be concise.
- Feedback should explain why the candidate received
  the score.
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    if text.startswith("```"):

        text = text.replace(
            "```json",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        text = text.strip()

    return json.loads(text)


# ==========================================================
# EVALUATE COMPLETE INTERVIEW
# ==========================================================

def evaluate_interview(results):

    prompt = f"""
You are a senior software engineering interviewer.

Below are all interview answers:

{results}

Evaluate the candidate's overall performance.

Return ONLY valid JSON.

{{
    "overall_feedback": "",
    "overall_strengths": [
        "",
        ""
    ],
    "overall_improvements": [
        "",
        ""
    ],
    "recommendation": ""
}}

Recommendation MUST be one of:

Highly Recommended
Recommended
Needs Improvement
Not Recommended
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    if text.startswith("```"):

        text = text.replace(
            "```json",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        text = text.strip()

    return json.loads(text)