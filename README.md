# Akira Prep — Interview Preparation Platform

Akira Prep is a web application for practicing technical and professional interviews.

## Features
- User registration and JWT login
- Fourteen subject areas with Easy, Intermediate and Hard question banks
- Persistent interview sessions and saved answers
- Rule-based answer scoring and per-question feedback
- Dashboard statistics and interview history
- PDF interview reports
- Responsive pink/purple cherry-blossom-inspired frontend

## Technology
Python, FastAPI, SQLAlchemy, SQLite, Pydantic, JWT, HTML, CSS, JavaScript,
Bootstrap, ECharts and ReportLab.

## Run locally
Use Python 3.10 or another compatible Python version.

1. Create an environment:
   `python3.10 -m venv .venv`
2. Activate it:
   `source .venv/bin/activate`
3. Install dependencies:
   `python -m pip install -r requirements.txt`
4. Create local configuration:
   `cp .env.example .env`
5. Start the API:
   `python -m uvicorn app.main:app --reload`
6. In another terminal, serve the frontend:
   `python3.10 -m http.server 5500 --directory frontend`
7. Open `http://127.0.0.1:5500`. API documentation is at
   `http://127.0.0.1:8000/docs`.

Keep both servers running.

## Seed question bank
Run `python seed_all_question_bank.py` to add missing starter questions.
The script preserves existing records and targets at least ten questions per
configured subject and difficulty. The seeded questions and answer guides are
starter material, not individually expert-reviewed assessment content.

## API smoke tests
Start the backend, then run `python test_api_flow.py`.
The test creates user and interview records, so use a development database.

## Scoring limitations
The interview answer endpoint currently uses rule-based keyword matching.
It is an MVP heuristic, not a validated assessment of candidate ability.
The Gemini service code should not be described as integrated into the main
answer flow until that integration is implemented and verified.

## Production readiness
Before public deployment, review JWT secret configuration, CORS restrictions,
database migrations, rate limiting, monitoring, scoring quality, security,
and end-to-end browser testing. Never commit `.env`, local databases, or keys.

## Status
The local API smoke-test suite has passed during development. Browser-based
end-to-end verification and a production security review are still needed.
