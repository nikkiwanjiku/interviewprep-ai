import json
import time
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000"
TOKEN = None
PASS_COUNT = 0
FAIL_COUNT = 0


def request(method, path, body=None, auth=False):
    headers = {"Content-Type": "application/json"}
    if auth and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_bytes = response.read()
            content_type = response.headers.get("Content-Type", "")

            if "application/pdf" in content_type.lower():
                payload = {
                    "content_type": content_type,
                    "bytes": len(raw_bytes),
                    "pdf_signature_ok": raw_bytes.startswith(b"%PDF-"),
                }
            else:
                raw = raw_bytes.decode("utf-8", errors="replace")
                try:
                    payload = json.loads(raw) if raw else None
                except json.JSONDecodeError:
                    payload = raw

            return response.status, payload
    except urllib.error.HTTPError as error:
        raw = error.read().decode()
        try:
            payload = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            payload = raw
        return error.code, payload
    except Exception as error:
        return 0, {"error": str(error)}


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"PASS  {name}" + (f" — {detail}" if detail else ""))
    else:
        FAIL_COUNT += 1
        print(f"FAIL  {name}" + (f" — {detail}" if detail else ""))


print("\n=== INTERVIEWPREP AI API TESTS ===\n")

# 1. Check the server
status, data = request("GET", "/")
check("Backend responds", status == 200, f"HTTP {status}")

# 2. Register a dedicated test account
# A unique email avoids conflicts with previous test runs.
email = f"api_test_{int(time.time())}@example.com"
password = "TestPassword_2026!"
user_data = {
    "full_name": "API Test User",
    "email": email,
    "password": password,
    "career_goal": "Software Engineer",
}

status, data = request("POST", "/auth/register", user_data)
check(
    "Register test user",
    status in (200, 201),
    f"HTTP {status}; {data}",
)

# 3. Log in
status, data = request(
    "POST", "/auth/login",
    {"email": email, "password": password},
)
if status == 200 and isinstance(data, dict):
    TOKEN = data.get("access_token")

check("Login returns access token", status == 200 and bool(TOKEN),
      f"HTTP {status}")

# 4. Verify invalid login is rejected
bad_status, _ = request(
    "POST", "/auth/login",
    {"email": email, "password": "definitely-wrong"},
)
check("Invalid password rejected", bad_status == 401,
      f"HTTP {bad_status}")

if TOKEN:
    # 5. Protected profile
    status, data = request("GET", "/users/profile", auth=True)
    check("Authenticated profile endpoint", status == 200,
          f"HTTP {status}")

    status, dashboard = request(
        "GET", "/interview/dashboard", auth=True
    )
    required = {
        "total_interviews",
        "completed_interviews",
        "in_progress_interviews",
        "average_score",
        "highest_score",
    }
    check(
        "Fetch dashboard statistics",
        status == 200 and isinstance(dashboard, dict)
        and required.issubset(dashboard.keys()),
        f"HTTP {status}; {dashboard}",
    )

    # 6. Fetch categories
    status, categories = request("GET", "/categories/")
    check("Fetch categories", status == 200 and isinstance(categories, list),
          f"HTTP {status}")

    # 7. Fetch questions
    status, questions = request("GET", "/questions/")
    check("Fetch questions", status == 200 and isinstance(questions, list),
          f"HTTP {status}")

    # Choose a category/difficulty combination with enough questions.
    selected = None
    if isinstance(questions, list) and isinstance(categories, list):
        category_ids = {c.get("id") for c in categories if isinstance(c, dict)}
        groups = {}
        for q in questions:
            if not isinstance(q, dict):
                continue
            cid = q.get("category_id")
            difficulty = q.get("difficulty")
            if cid in category_ids and difficulty:
                key = (cid, str(difficulty))
                groups.setdefault(key, []).append(q)
        if groups:
            selected = max(groups.items(), key=lambda item: len(item[1]))

    if selected:
        (category_id, difficulty), available_questions = selected
        question_count = 1

        print(f"\nUsing category={category_id}, difficulty={difficulty!r}")

        # 8. Start a one-question interview
        status, interview_data = request(
            "POST", "/interview/start",
            {
                "category_id": category_id,
                "difficulty": difficulty,
                "question_count": question_count,
            },
            auth=True,
        )

        interview_id = (
            interview_data.get("interview_id")
            if isinstance(interview_data, dict) else None
        )
        check("Start interview", status in (200, 201) and interview_id is not None,
              f"HTTP {status}; {interview_data}")

        if interview_id is not None:
            # 9. Retrieve the selected interview questions
            status, interview_questions = request(
                "GET", f"/interview/{interview_id}/questions", auth=True
            )
            check(
                "Fetch interview questions",
                status == 200 and isinstance(interview_questions, list)
                and len(interview_questions) >= 1,
                f"HTTP {status}",
            )

            if status == 200 and isinstance(interview_questions, list) and interview_questions:
                question = interview_questions[0]
                question_id = question.get("id", question.get("question_id"))

                if question_id is not None:
                    # 10. Submit an answer
                    status, answer_result = request(
                        "POST", f"/interview/{interview_id}/answer",
                        {
                            "question_id": question_id,
                            "answer": (
                                "I would clarify the requirements, break the problem "
                                "into manageable steps, implement a solution, test it, "
                                "and communicate the outcome to the team."
                            ),
                        },
                        auth=True,
                    )
                    check("Submit answer", status == 200,
                          f"HTTP {status}; {answer_result}")

                    # 11. Check interview details
                    status, details = request(
                        "GET", f"/interview/{interview_id}", auth=True
                    )
                    check("Fetch interview details", status == 200,
                          f"HTTP {status}")

                    # 12. Check result endpoint
                    status, result = request(
                        "GET", f"/interview/{interview_id}/result", auth=True
                    )
                    check("Fetch interview result", status == 200,
                          f"HTTP {status}")
                else:
                    check("Question has an ID", False, str(question))

            # 13. History
            status, history = request("GET", "/interview/history", auth=True)
            check("Fetch interview history", status == 200,
                  f"HTTP {status}")

            # 14. Report endpoint
            status, report = request(
                "GET", f"/report/{interview_id}", auth=True
            )
            check(
                "Download valid PDF report",
                status == 200
                and isinstance(report, dict)
                and report.get("content_type", "").lower().startswith("application/pdf")
                and report.get("bytes", 0) > 5
                and report.get("pdf_signature_ok") is True,
                f"HTTP {status}; {report}",
            )
    else:
        check(
            "Find category with available questions",
            False,
            "No matching category/difficulty questions were found. "
            "Check seed data and question response fields.",
        )

    # 15. Verify unauthenticated access is denied
    status, _ = request("GET", "/users/profile")
    check("Protected profile rejects anonymous request",
          status in (401, 403), f"HTTP {status}")

print("\n=== SUMMARY ===")
print(f"Passed: {PASS_COUNT}")
print(f"Failed: {FAIL_COUNT}")
print(f"Total:  {PASS_COUNT + FAIL_COUNT}")
print("\nNote: interview tests create a test account and interview in your database.")
