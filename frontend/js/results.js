const token = localStorage.getItem("token");
const params = new URLSearchParams(window.location.search);
const interviewId = params.get("id");

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value ?? "";
    }
}

function toItems(value) {
    if (value == null || value === "") return [];

    if (Array.isArray(value)) {
        return value.flatMap(toItems);
    }

    if (typeof value === "string") {
        const text = value.trim();
        if (!text) return [];

        // Support JSON-encoded lists or strings from the API.
        if (
            (text.startsWith("[") && text.endsWith("]")) ||
            (text.startsWith('"') && text.endsWith('"'))
        ) {
            try {
                const parsed = JSON.parse(text);
                if (parsed !== value) return toItems(parsed);
            } catch {
                // Keep the original text if it is not valid JSON.
            }
        }

        return [text];
    }

    return [String(value)];
}

function renderList(id, values, emptyMessage) {
    const list = document.getElementById(id);
    if (!list) return;

    list.replaceChildren();

    const items = toItems(values);

    if (items.length === 0) {
        const li = document.createElement("li");
        li.textContent = emptyMessage;
        list.appendChild(li);
        return;
    }

    for (const item of items) {
        const li = document.createElement("li");
        li.textContent = item;
        list.appendChild(li);
    }
}

function appendField(container, label, value) {
    const paragraph = document.createElement("p");
    const heading = document.createElement("strong");

    heading.textContent = `${label}:`;
    paragraph.appendChild(heading);
    paragraph.appendChild(document.createElement("br"));
    paragraph.appendChild(
        document.createTextNode(value || "Not available.")
    );

    container.appendChild(paragraph);
}

function displayResults(data) {
    const answers = Array.isArray(data.answers) ? data.answers : [];

    const answerScore = answers.reduce(
        (total, answer) => total + (Number(answer.score) || 0),
        0
    );

    const totalScore =
        data.total_score != null
            ? Number(data.total_score)
            : answerScore;

    const questionCount =
        Number(data.question_count) || answers.length;

    const maximumScore = questionCount * 10;

    const percentage =
        maximumScore > 0
            ? (totalScore / maximumScore) * 100
            : 0;

    setText(
        "overallScore",
        `Overall Score: ${percentage.toFixed(1)}% (${totalScore}/${maximumScore} points)`
    );

    setText(
        "overallFeedback",
        "Review the question-by-question feedback below to understand your performance."
    );

    const strengths = [...new Set(answers.flatMap(
        answer => toItems(answer.strengths)
    ))];

    const improvements = [...new Set(answers.flatMap(
        answer => toItems(answer.improvements)
    ))];

    renderList(
        "strengths",
        strengths,
        "No strengths recorded for this interview."
    );

    renderList(
        "improvements",
        improvements,
        "No improvement notes recorded for this interview."
    );

    setText(
        "recommendation",
        "Review the improvement notes and compare your answers with the ideal answers before your next practice interview."
    );

    const container = document.getElementById("answers");
    if (!container) return;

    container.replaceChildren();

    if (answers.length === 0) {
        container.textContent = "No submitted answers were found.";
        return;
    }

    answers.forEach((answer, index) => {
        const card = document.createElement("div");
        card.className = "card mt-4";

        const body = document.createElement("div");
        body.className = "card-body";

        const title = document.createElement("h5");
        title.textContent = `Question ${index + 1}: ${
            answer.question || "Question unavailable."
        }`;

        body.appendChild(title);

        appendField(body, "Your Answer", answer.your_answer);
        appendField(body, "Score", `${Number(answer.score) || 0}/10`);
        appendField(body, "Feedback", answer.feedback);
        appendField(
            body,
            "Strengths",
            toItems(answer.strengths).join(" • ")
        );
        appendField(
            body,
            "Areas for Improvement",
            toItems(answer.improvements).join(" • ")
        );
        appendField(body, "Ideal Answer", answer.ideal_answer);

        card.appendChild(body);
        container.appendChild(card);
    });
}

async function loadResults() {
    if (!token) {
        window.location.href = "login.html";
        return;
    }

    if (!interviewId) {
        setText("overallFeedback", "No interview ID was supplied in the page URL.");
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/interview/${encodeURIComponent(interviewId)}/result`,
            {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {
            setText(
                "overallFeedback",
                data.detail || "Unable to load interview results."
            );
            return;
        }

        displayResults(data);
    } catch (error) {
        console.error("Unable to load results:", error);
        setText(
            "overallFeedback",
            "Could not connect to the server. Check that the backend is running."
        );
    }
}

const dashboardButton = document.getElementById("dashboardBtn");
if (dashboardButton) {
    dashboardButton.addEventListener("click", () => {
        window.location.href = "dashboard.html";
    });
}

const retryButton = document.getElementById("retryBtn");
if (retryButton) {
    retryButton.addEventListener("click", () => {
        window.location.href = "interview-setup.html";
    });
}

const downloadButton = document.getElementById("downloadBtn");
if (downloadButton) {
    downloadButton.addEventListener("click", async () => {
        if (!token || !interviewId) return;

        downloadButton.disabled = true;

        try {
            const response = await fetch(
                `${API_URL}/report/${encodeURIComponent(interviewId)}`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            if (!response.ok) {
                alert("Unable to download the interview report.");
                return;
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");

            link.href = url;
            link.download = `akira_prep_report_${interviewId}.pdf`;

            document.body.appendChild(link);
            link.click();
            link.remove();

            window.setTimeout(
                () => window.URL.revokeObjectURL(url),
                1000
            );
        } catch (error) {
            console.error("Report download failed:", error);
            alert("Could not download the report. Check the server connection.");
        } finally {
            downloadButton.disabled = false;
        }
    });
}

loadResults();
