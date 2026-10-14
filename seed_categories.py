from app.database import SessionLocal
from app.models.category import Category


categories = [
    {
        "name": "Python Backend",
        "description": (
            "Python backend development including Python, FastAPI, REST APIs, "
            "SQL, databases, authentication, JWT, APIs, backend architecture, "
            "debugging, and server-side development."
        )
    },
    {
        "name": "Frontend Web",
        "description": (
            "Frontend web development including HTML, CSS, JavaScript, React, "
            "Next.js, APIs, state management, browser fundamentals, and web performance."
        )
    },
    {
        "name": "Mobile Development",
        "description": (
            "Mobile application development including Flutter, Dart, UI development, "
            "state management, API integration, navigation, performance, and mobile architecture."
        )
    },
    {
        "name": "Cybersecurity",
        "description": (
            "Cybersecurity including authentication, authorization, JWT, encryption, "
            "OWASP, common vulnerabilities, secure coding, network security, and application security."
        )
    },
    {
        "name": "Quality Assurance",
        "description": (
            "Software quality assurance including manual testing, test cases, automation, "
            "API testing, Cypress, regression testing, integration testing, and test strategy."
        )
    },
    {
        "name": "Product Management",
        "description": (
            "Product management including product requirements, user stories, prioritization, "
            "Agile, Scrum, product metrics, roadmaps, stakeholder management, and product strategy."
        )
    },
    {
        "name": "UX Design",
        "description": (
            "UX design including user flows, wireframes, prototypes, usability, design systems, "
            "interaction design, accessibility, visual hierarchy, and user-centered design."
        )
    },
    {
        "name": "UX Research",
        "description": (
            "UX research including research planning, interviews, surveys, usability testing, "
            "personas, research synthesis, qualitative and quantitative methods, and insights."
        )
    },
    {
        "name": "Software Engineering",
        "description": (
            "General software engineering including Git, software development lifecycle, "
            "software architecture, debugging, APIs, design patterns, system design, "
            "code quality, maintainability, and engineering practices."
        )
    },
    {
        "name": "Data / AI & Machine Learning",
        "description": (
            "Data, artificial intelligence, and machine learning including machine learning "
            "fundamentals, datasets, model evaluation, AI systems, LLMs, RAG, embeddings, "
            "model deployment, and responsible AI."
        )
    },
    {
        "name": "Data Engineering",
        "description": (
            "Data engineering including SQL, ETL and ELT, data pipelines, databases, "
            "data warehouses, APIs, data quality, batch processing, streaming, and data architecture."
        )
    },
    {
        "name": "UI Engineering",
        "description": (
            "UI engineering including design systems, reusable components, responsive interfaces, "
            "accessibility, CSS, frontend architecture, design-to-code implementation, "
            "UI performance, and component-driven development."
        )
    },
    {
        "name": "DevOps & Cloud",
        "description": (
            "DevOps and cloud engineering including CI/CD, Docker, deployment, cloud fundamentals, "
            "environment management, monitoring, infrastructure, automation, and reliability."
        )
    }
]


def seed_categories():
    db = SessionLocal()

    try:
        for category_data in categories:

            existing = (
                db.query(Category)
                .filter(Category.name == category_data["name"])
                .first()
            )

            if existing:
                print(f"Already exists: {category_data['name']}")
                continue

            category = Category(**category_data)

            db.add(category)

            print(f"Added: {category_data['name']}")

        db.commit()

        print("\nCategory seeding completed successfully.")

    except Exception as error:

        db.rollback()

        print(f"Error while seeding categories: {error}")

    finally:

        db.close()


if __name__ == "__main__":
    seed_categories()
