from fastapi import FastAPI

app = FastAPI(
    title="InterviewPrep AI",
    version="1.0.0",
    description="Practice smarter. Interview with confidence."
)


@app.get("/")
def home():
    return {
        "message": "Welcome to InterviewPrep AI 🚀"
    }