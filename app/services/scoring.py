def calculate_score(user_answer: str, expected_answer: str):
    """
    Temporary scoring algorithm.
    Later this will be replaced with Gemini AI.
    """

    user = user_answer.lower()
    expected = expected_answer.lower()

    matching_words = sum(
        1 for word in expected.split()
        if word in user
    )

    score = min(matching_words, 10)

    if score >= 8:
        feedback = "Excellent answer."
    elif score >= 5:
        feedback = "Good answer, but add more technical detail."
    else:
        feedback = "Needs improvement."

    return score, feedback
import json


def evaluate_interview(results):

    prompt = f"""
You are an expert technical interviewer.

Below are all interview answers.

{results}

Return ONLY valid JSON.

{{
    "overall_feedback":"",

    "overall_strengths":[
        "",
        ""
    ],

    "overall_improvements":[
        "",
        ""
    ],

    "recommendation":""
}}

Recommendation must be one of

Highly Recommended
Recommended
Needs Improvement
Not Recommended
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")

    return json.loads(text)