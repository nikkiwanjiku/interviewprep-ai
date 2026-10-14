document.addEventListener("DOMContentLoaded", () => {

    const questionsGrid = document.getElementById("questionsGrid");
    const emptyState = document.getElementById("emptyState");
    const questionCount = document.getElementById("questionCount");

    const searchInput = document.getElementById("searchInput");
    const topicFilter = document.getElementById("topicFilter");
    const difficultyFilter = document.getElementById("difficultyFilter");
    const clearFilters = document.getElementById("clearFilters");

    const topicPills = document.querySelectorAll(".topic-pill");

    let allQuestions = [];

    async function loadQuestions() {

        questionsGrid.innerHTML = `
            <div class="question-loading">
                <div class="spinner-border" role="status"></div>
                <p>Loading your questions...</p>
            </div>
        `;

        try {

            const response = await fetch(`${API_URL}/questions/`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            allQuestions = await response.json();

            renderQuestions();

        } catch (error) {

            console.error("Question Bank error:", error);

            questionsGrid.innerHTML = `
                <div class="question-error">
                    <div class="error-icon">🌸</div>
                    <h3>We couldn't load the questions</h3>
                    <p>
                        Please make sure the Akira Prep backend is running
                        and try again.
                    </p>
                    <button class="clear-btn" onclick="location.reload()">
                        Try Again
                    </button>
                </div>
            `;

            questionCount.textContent = "Unable to load";

        }
    }


    function getCategoryName(question) {

        if (question.category && question.category.name) {
            return question.category.name;
        }

        const categoryMap = {
            1: "Frontend Web",
            2: "Python Backend",
            3: "Data Engineering"
        };

        return categoryMap[question.category_id] || "Frontend Web";
    }


    function normalizeDifficulty(difficulty) {

        if (!difficulty) {
            return "Easy";
        }

        return String(difficulty)
            .charAt(0)
            .toUpperCase() +
            String(difficulty).slice(1).toLowerCase();
    }


    function getDifficultyClass(difficulty) {

        return normalizeDifficulty(difficulty)
            .toLowerCase();
    }


    function renderQuestions() {

        const searchTerm =
            searchInput.value.trim().toLowerCase();

        const selectedTopic =
            topicFilter.value;

        const selectedDifficulty =
            difficultyFilter.value.toLowerCase();


        const filteredQuestions =
            allQuestions.filter(question => {

                const text =
                    `${question.question || ""} ${question.expected_answer || ""}`
                    .toLowerCase();

                const category =
                    getCategoryName(question);

                const categoryMatches =
                    selectedTopic === "all" ||
                    category === selectedTopic ||
                    (
                        selectedTopic === "HTML & CSS" &&
                        (
                            category.includes("HTML") ||
                            category.includes("CSS") ||
                            category.includes("Frontend")
                        )
                    );

                const difficultyMatches =
                    selectedDifficulty === "all" ||
                    String(question.difficulty || "")
                        .toLowerCase() === selectedDifficulty;

                const searchMatches =
                    !searchTerm ||
                    text.includes(searchTerm) ||
                    category.toLowerCase().includes(searchTerm);

                return (
                    categoryMatches &&
                    difficultyMatches &&
                    searchMatches
                );

            });


        questionCount.textContent =
            `${filteredQuestions.length} ${
                filteredQuestions.length === 1
                    ? "question"
                    : "questions"
            }`;


        if (!filteredQuestions.length) {

            questionsGrid.innerHTML = "";

            emptyState.classList.remove("d-none");

            return;
        }


        emptyState.classList.add("d-none");


        questionsGrid.innerHTML =
            filteredQuestions
                .map((question, index) =>
                    createQuestionCard(question, index)
                )
                .join("");

    }


    function createQuestionCard(question, index) {

        const category =
            getCategoryName(question);

        const difficulty =
            normalizeDifficulty(question.difficulty);

        const difficultyClass =
            getDifficultyClass(question.difficulty);

        const questionText =
            escapeHtml(question.question || "Question unavailable");

        const expectedAnswer =
            escapeHtml(question.expected_answer || "");

        const points =
            question.points ?? 10;


        return `
            <article class="question-card">

                <div class="question-card-top">

                    <span class="question-number">
                        ${String(index + 1).padStart(2, "0")}
                    </span>

                    <span class="difficulty-badge ${difficultyClass}">
                        ${difficulty}
                    </span>

                </div>


                <div class="question-card-body">

                    <span class="question-category">
                        <i class="bi bi-bookmark-heart-fill"></i>
                        ${escapeHtml(category)}
                    </span>

                    <h3>
                        ${questionText}
                    </h3>

                    <div class="question-meta">

                        <span>
                            <i class="bi bi-star-fill"></i>
                            ${points} points
                        </span>

                        <span>
                            <i class="bi bi-clock"></i>
                            Interview Practice
                        </span>

                    </div>

                </div>


                <details class="answer-preview">

                    <summary>
                        <span>
                            <i class="bi bi-lightbulb-fill"></i>
                            View ideal answer
                        </span>

                        <i class="bi bi-chevron-down"></i>
                    </summary>

                    <div class="ideal-answer">
                        ${expectedAnswer}
                    </div>

                </details>


                <div class="question-card-footer">

                    <span>
                        Ready to practice?
                    </span>

                    <a
                        href="interview-setup.html"
                        class="practice-question-btn"
                    >
                        Practice
                        <i class="bi bi-arrow-right"></i>
                    </a>

                </div>

            </article>
        `;
    }


    function escapeHtml(value) {

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    searchInput.addEventListener(
        "input",
        renderQuestions
    );

    topicFilter.addEventListener(
        "change",
        renderQuestions
    );

    difficultyFilter.addEventListener(
        "change",
        renderQuestions
    );


    topicPills.forEach(pill => {

        pill.addEventListener("click", () => {

            topicPills.forEach(item =>
                item.classList.remove("active")
            );

            pill.classList.add("active");

            topicFilter.value =
                pill.dataset.topic;

            renderQuestions();

        });

    });


    clearFilters.addEventListener("click", () => {

        searchInput.value = "";

        topicFilter.value = "all";

        difficultyFilter.value = "all";

        topicPills.forEach(pill =>
            pill.classList.remove("active")
        );

        const allPill =
            document.querySelector(
                '.topic-pill[data-topic="all"]'
            );

        if (allPill) {
            allPill.classList.add("active");
        }

        renderQuestions();

    });


    loadQuestions();

});
