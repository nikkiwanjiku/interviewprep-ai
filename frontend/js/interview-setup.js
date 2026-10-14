const token = localStorage.getItem("token");

const categorySelect = document.getElementById("category");
const difficultySelect = document.getElementById("difficulty");
const questionCountSelect = document.getElementById("questionCount");
const startBtn = document.getElementById("startBtn");

const MIN_SESSION_QUESTIONS = 5;
const STANDARD_COUNTS = [5, 10, 15, 20];

const availableQuestions = new Map();
let originalStartButtonHtml = "";

if (startBtn) {
    originalStartButtonHtml = startBtn.innerHTML;
    startBtn.disabled = true;
}

if (!token) {
    window.location.href = "login.html";
}

function setOptions(select, placeholder, options) {
    if (!select) return;

    select.replaceChildren(new Option(placeholder, ""));

    for (const option of options) {
        select.add(
            new Option(option.label, option.value)
        );
    }
}

function currentCategoryDifficulties() {
    return availableQuestions.get(String(categorySelect?.value)) || new Map();
}

function refreshStartButton() {
    if (!startBtn) return;

    startBtn.disabled = !(
        token &&
        categorySelect?.value &&
        difficultySelect?.value &&
        Number(questionCountSelect?.value) >= MIN_SESSION_QUESTIONS
    );
}

function updateQuestionCountOptions() {
    const difficulties = currentCategoryDifficulties();
    const selectedDifficulty = String(difficultySelect?.value || "").toLowerCase();
    const entry = difficulties.get(selectedDifficulty);

    if (!entry || !questionCountSelect) {
        setOptions(questionCountSelect, "Select question count", []);
        if (questionCountSelect) questionCountSelect.disabled = true;
        refreshStartButton();
        return;
    }

    const previousCount = Number(questionCountSelect.value);
    let counts = STANDARD_COUNTS.filter(
        count => count <= entry.count
    );

    if (counts.length === 0 && entry.count >= MIN_SESSION_QUESTIONS) {
        counts = [entry.count];
    }

    setOptions(
        questionCountSelect,
        "Select question count",
        counts.map(count => ({
            value: String(count),
            label: `${count} questions`
        }))
    );

    questionCountSelect.disabled = counts.length === 0;

    if (counts.includes(previousCount)) {
        questionCountSelect.value = String(previousCount);
    } else if (counts.includes(10)) {
        questionCountSelect.value = "10";
    } else if (counts.length) {
        questionCountSelect.value = String(counts[0]);
    }

    refreshStartButton();
}

function updateDifficultyOptions() {
    const current = String(difficultySelect?.value || "").toLowerCase();
    const difficulties = currentCategoryDifficulties();

    const options = [...difficulties.entries()]
        .filter(([, entry]) => entry.count >= MIN_SESSION_QUESTIONS)
        .sort((a, b) => a[1].label.localeCompare(b[1].label))
        .map(([key, entry]) => ({
            value: key,
            label: entry.label
        }));

    setOptions(difficultySelect, "Select difficulty", options);

    if (options.some(option => option.value === current)) {
        difficultySelect.value = current;
    } else if (options.length) {
        difficultySelect.value = options[0].value;
    }

    updateQuestionCountOptions();
}

async function loadSetupOptions() {
    if (!categorySelect || !difficultySelect || !questionCountSelect || !startBtn) {
        console.error("Interview setup is missing one or more required form elements.");
        return;
    }

    try {
        const [categoryResponse, questionResponse] = await Promise.all([
            fetch(`${API_URL}/categories/`),
            fetch(`${API_URL}/questions/`)
        ]);

        if (!categoryResponse.ok || !questionResponse.ok) {
            throw new Error("Unable to load categories or questions.");
        }

        const categories = await categoryResponse.json();
        const questions = await questionResponse.json();

        availableQuestions.clear();

        for (const question of questions) {
            if (question.category_id == null || !question.difficulty) continue;

            const categoryId = String(question.category_id);
            const key = String(question.difficulty).trim().toLowerCase();

            if (!availableQuestions.has(categoryId)) {
                availableQuestions.set(categoryId, new Map());
            }

            const difficulties = availableQuestions.get(categoryId);

            if (!difficulties.has(key)) {
                difficulties.set(key, {
                    label: String(question.difficulty).trim(),
                    count: 0
                });
            }

            difficulties.get(key).count += 1;
        }

        const supportedCategories = categories.filter(category => {
            const difficulties = availableQuestions.get(String(category.id));
            return difficulties &&
                [...difficulties.values()].some(
                    entry => entry.count >= MIN_SESSION_QUESTIONS
                );
        });

        setOptions(
            categorySelect,
            supportedCategories.length
                ? "Select an interview category"
                : "No categories have enough questions",
            supportedCategories.map(category => ({
                value: String(category.id),
                label: category.name
            }))
        );

        if (supportedCategories.length === 0) {
            setOptions(difficultySelect, "No available difficulties", []);
            setOptions(questionCountSelect, "No available question counts", []);
            alert("There are no interview categories with at least five questions yet.");
            return;
        }

        categorySelect.disabled = false;
        difficultySelect.disabled = false;
        questionCountSelect.disabled = false;

        categorySelect.addEventListener("change", updateDifficultyOptions);
        difficultySelect.addEventListener("change", updateQuestionCountOptions);

        updateDifficultyOptions();
        refreshStartButton();

    } catch (error) {
        console.error("Interview setup loading failed:", error);
        alert("Unable to load interview options. Check that the backend is running.");
    }
}

async function startInterview(event) {
    event?.preventDefault();

    if (!token) {
        window.location.href = "login.html";
        return;
    }

    const categoryId = Number(categorySelect.value);
    const difficulty = difficultySelect.value;
    const questionCount = Number(questionCountSelect.value);

    if (!categoryId || !difficulty || questionCount < MIN_SESSION_QUESTIONS) {
        alert("Select a valid category, difficulty, and question count.");
        return;
    }

    startBtn.disabled = true;
    startBtn.textContent = "Preparing Interview...";

    try {
        const response = await fetch(`${API_URL}/interview/start`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                category_id: categoryId,
                difficulty,
                question_count: questionCount
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Unable to start interview.");
            return;
        }

        if (!data.interview_id) {
            alert("The server did not return an interview ID.");
            return;
        }

        localStorage.setItem("currentInterviewId", String(data.interview_id));
        window.location.href = "interview.html";

    } catch (error) {
        console.error("Interview start failed:", error);
        alert("Could not start the interview. Please check the server connection.");
    } finally {
        startBtn.innerHTML = originalStartButtonHtml;
        refreshStartButton();
    }
}

if (startBtn) {
    startBtn.addEventListener("click", startInterview);
}

loadSetupOptions();
