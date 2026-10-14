from sqlalchemy import func

from app.database import get_db
from app.models.category import Category
from app.models.question import Question

TARGET = 10

TOPICS = {
    "Cybersecurity": [
        "threat modelling", "authentication and authorization",
        "secure password storage", "input validation",
        "SQL injection prevention", "cross-site scripting prevention",
        "CSRF protection", "encryption in transit and at rest",
        "secrets management", "incident response and security logging",
    ],
    "Data / AI & Machine Learning": [
        "training validation and test splits", "feature engineering",
        "data leakage prevention", "classification metrics",
        "regression evaluation metrics", "overfitting and regularization",
        "model bias and fairness", "model drift monitoring",
        "model deployment and inference", "model explainability",
    ],
    "Data Engineering": [
        "ETL and ELT pipelines", "data quality validation",
        "schema evolution", "batch versus streaming processing",
        "idempotent data pipelines", "partitioning and indexing",
        "workflow orchestration and retries", "data lineage",
        "data warehouses and lakehouses", "late-arriving events",
    ],
    "DevOps & Cloud": [
        "continuous integration and delivery", "containerization",
        "environment configuration", "infrastructure as code",
        "metrics logs and distributed traces", "deployment rollback",
        "secrets management", "autoscaling",
        "least-privilege cloud access", "disaster recovery",
    ],
    "Frontend Web": [
        "semantic HTML and accessibility", "responsive layouts",
        "frontend state management", "form validation",
        "API loading and error states", "safe browser storage",
        "web performance optimization", "cross-browser testing",
        "client-side routing", "reusable components",
    ],
    "Mobile Development": [
        "mobile application lifecycle", "offline state handling",
        "network errors in mobile apps", "secure token storage",
        "mobile accessibility", "application state management",
        "battery and performance optimization", "app signing and releases",
        "runtime permissions", "device and OS fragmentation",
    ],
    "Product Management": [
        "customer problem discovery", "user personas",
        "product outcomes and metrics", "requirements definition",
        "MoSCoW prioritization", "minimum viable product scope",
        "experimentation and A/B tests", "roadmap prioritization",
        "product analytics", "customer feedback synthesis",
    ],
    "Programming": [
        "data structures and algorithm complexity", "error handling",
        "modular program design", "unit testing",
        "concurrency and race conditions", "types and input validation",
        "debugging techniques", "resource and memory management",
        "API design", "safe code refactoring",
    ],
    "Python Backend": [
        "FastAPI route design", "Pydantic request validation",
        "SQLAlchemy sessions and relationships", "database transactions",
        "JWT authentication", "dependency injection",
        "async request handling", "database migrations",
        "integration testing", "exception handling and logging",
    ],
    "Quality Assurance": [
        "test case design", "boundary value analysis",
        "equivalence partitioning", "regression testing",
        "REST API testing", "flaky automation tests",
        "reproducible defect reports", "risk-based testing",
        "exploratory testing", "continuous integration test suites",
    ],
    "Software Engineering": [
        "software architecture patterns", "SOLID principles",
        "code review practices", "version control workflows",
        "the test pyramid", "requirements traceability",
        "architecture trade-offs", "security by design",
        "reliable deployment strategies", "technical debt refactoring",
    ],
    "UI Engineering": [
        "design system architecture", "design tokens",
        "accessible reusable components", "responsive layout systems",
        "loading empty and error states", "visual regression testing",
        "typography hierarchy", "maintainable CSS architecture",
        "rendering performance", "cross-device consistency",
    ],
    "UX Design": [
        "user interviews", "customer journey mapping",
        "information architecture", "usability testing",
        "accessible interaction design", "prototyping",
        "error prevention and recovery", "design system consistency",
        "responsive interactions", "behavioral success metrics",
    ],
    "UX Research": [
        "research question formulation", "participant sampling",
        "neutral interview questions", "moderated usability sessions",
        "qualitative data coding", "survey question bias",
        "research method triangulation", "participant consent and privacy",
        "research synthesis", "ethical reporting of findings",
    ],
}


def make_question(category, topic, difficulty):
    if difficulty == "Easy":
        prompt = (
            f"Explain {topic} in {category}. Describe its purpose, "
            "the key concepts or steps, and one practical example."
        )
        guide = (
            f"A good answer defines {topic} accurately in the context of "
            f"{category}, explains why it matters, identifies the main "
            "concepts or steps, and gives a clear practical example."
        )
    elif difficulty == "Intermediate":
        prompt = (
            f"A team is applying {topic} in a {category} project. "
            "Outline your approach, the tools or methods you would choose, "
            "edge cases to cover, and how you would verify the result."
        )
        guide = (
            f"A strong answer explains how to apply {topic} in {category}, "
            "sets out a logical sequence of actions, selects suitable "
            "techniques, covers edge cases, discusses trade-offs, and "
            "defines tests or acceptance criteria to verify the outcome."
        )
    else:
        prompt = (
            f"Design and defend a production-ready approach to {topic} "
            f"for a {category} system under reliability, security, "
            "performance, and delivery constraints. Compare alternatives, "
            "identify failure modes, define measurable acceptance criteria, "
            "and describe recovery or mitigation."
        )
        guide = (
            f"A strong answer proposes and justifies a production-ready "
            f"approach to {topic} in {category}. It states assumptions and "
            "constraints, compares alternatives, addresses reliability, "
            "security, performance, and maintainability, identifies failure "
            "modes, and defines measurable validation and recovery plans."
        )

    return prompt, guide


def seed():
    generator = get_db()
    db = next(generator)
    summary = []

    try:
        categories = db.query(Category).order_by(Category.name).all()
        categories_by_name = {
            category.name.strip().casefold(): category
            for category in categories
        }

        missing_categories = [
            name for name in TOPICS
            if name.casefold() not in categories_by_name
        ]

        if missing_categories:
            print("WARNING: These configured categories were not found:")
            for name in missing_categories:
                print(f"  - {name}")

        for name, topics in TOPICS.items():
            category = categories_by_name.get(name.casefold())
            if category is None:
                continue

            for difficulty in ("Easy", "Intermediate", "Hard"):
                existing_count = (
                    db.query(func.count(Question.id))
                    .filter(
                        Question.category_id == category.id,
                        func.lower(Question.difficulty) == difficulty.casefold(),
                    )
                    .scalar() or 0
                )

                if existing_count >= TARGET:
                    summary.append((name, difficulty, existing_count, 0))
                    continue

                known_questions = {
                    text.strip().casefold()
                    for (text,) in db.query(Question.question)
                    .filter(
                        Question.category_id == category.id,
                        func.lower(Question.difficulty) == difficulty.casefold(),
                    )
                    .all()
                }

                added = 0

                for topic in topics:
                    prompt, guide = make_question(name, topic, difficulty)

                    if prompt.casefold() in known_questions:
                        continue

                    db.add(Question(
                        question=prompt,
                        expected_answer=guide,
                        difficulty=difficulty,
                        points=10,
                        category_id=category.id,
                    ))
                    known_questions.add(prompt.casefold())
                    added += 1

                    if existing_count + added >= TARGET:
                        break

                db.flush()
                summary.append((name, difficulty, existing_count + added, added))

        db.commit()

        print("\nQUESTION BANK SEED REPORT")
        print("=" * 76)

        all_ok = True

        for name, difficulty, count, added in summary:
            status = "OK" if count >= TARGET else "NEEDS MORE"
            if count < TARGET:
                all_ok = False

            print(
                f"{status:11} | {name:31} | {difficulty:12} "
                f"| total={count:2} | added={added:2}"
            )

        print("=" * 76)
        print(f"Categories configured: {len(TOPICS)}")
        print(f"Category/difficulty combinations checked: {len(summary)}")
        print("Result:", "All combinations meet the target." if all_ok
              else "Some combinations still need questions.")
        print("Existing questions were preserved.")

    except Exception:
        db.rollback()
        raise
    finally:
        generator.close()


if __name__ == "__main__":
    seed()
