console.log("Dashboard loaded.");

/* ==========================================================
   AUTHENTICATION
========================================================== */

const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "login.html";
}


/* ==========================================================
   GREETING
========================================================== */

function updateGreeting() {

    const greeting =
        document.getElementById("greeting");

    if (!greeting) return;

    const hour =
        new Date().getHours();

    if (hour < 12) {

        greeting.textContent =
            "☀️ Good Morning!";

    } else if (hour < 18) {

        greeting.textContent =
            "🌸 Good Afternoon!";

    } else {

        greeting.textContent =
            "🌙 Good Evening!";
    }
}


/* ==========================================================
   MOTIVATION
========================================================== */

const motivations = [

    "🌸 Every interview gets you closer to your dream job.",

    "💖 Confidence is built through practice.",

    "✨ Small improvements lead to big opportunities.",

    "🚀 Today's practice is tomorrow's success.",

    "🎯 Keep learning. Keep growing.",

    "🌷 Believe in yourself — you've got this."
];


function updateMotivation() {

    const element =
        document.getElementById(
            "motivationMessage"
        );

    if (!element) return;

    const randomIndex =
        Math.floor(
            Math.random() *
            motivations.length
        );

    element.textContent =
        motivations[randomIndex];
}


/* ==========================================================
   LOAD DASHBOARD STATISTICS
========================================================== */

async function loadDashboard() {

    try {

        const response =
            await fetch(
                `${API_URL}/interview/dashboard`,
                {
                    method: "GET",

                    headers: {
                        Authorization:
                            `Bearer ${token}`
                    }
                }
            );


        if (response.status === 401) {

            localStorage.removeItem("token");

            window.location.href =
                "login.html";

            return;
        }


        const data =
            await response.json();


        if (!response.ok) {

            console.error(
                "Dashboard error:",
                data
            );

            return;
        }


        const totalInterviews =
            document.getElementById(
                "totalInterviews"
            );

        if (totalInterviews) {

            totalInterviews.textContent =
                data.total_interviews ?? 0;
        }


        const completedInterviews =
            document.getElementById(
                "completedInterviews"
            );

        if (completedInterviews) {

            completedInterviews.textContent =
                data.completed_interviews ?? 0;
        }


        const averageScore =
            document.getElementById(
                "averageScore"
            );

        if (averageScore) {

            averageScore.textContent =
                `${Number(String(data.average_score ?? 0).replace(/%/g, "")).toFixed(1)}%`;
        }


        const highestScore =
            document.getElementById(
                "highestScore"
            );

        if (highestScore) {

            highestScore.textContent =
                `${Number(String(data.highest_score ?? 0).replace(/%/g, "")).toFixed(0)}%`;
        }


        /*
         * The backend already tells us how many
         * interviews are currently IN_PROGRESS.
         */

        updateContinueInterviewVisibility(
            data.in_progress_interviews ?? 0
        );

    }

    catch (error) {

        console.error(
            "Unable to load dashboard:",
            error
        );
    }
}


/* ==========================================================
   CONTINUE INTERVIEW
========================================================== */

function updateContinueInterviewVisibility(
    count
) {

    const button =
        document.getElementById(
            "continueInterviewBtn"
        );

    if (!button) return;


    if (count > 0) {

        button.classList.remove(
            "d-none"
        );

    } else {

        button.classList.add(
            "d-none"
        );
    }
}


/* ==========================================================
   OPEN AN EXISTING INTERVIEW
========================================================== */

function continueInterview(interviewId) {

    if (!interviewId) {

        console.error(
            "No interview ID supplied."
        );

        return;
    }


    /*
     * interview.js already expects this
     * localStorage value.
     */

    localStorage.setItem(
        "currentInterviewId",
        String(interviewId)
    );


    window.location.href =
        "interview.html";
}


/* ==========================================================
   LOAD INTERVIEW HISTORY
========================================================== */

async function loadHistory() {

    const historyTable =
        document.getElementById(
            "historyTable"
        );

    if (!historyTable) return;


    try {

        const response =
            await fetch(
                `${API_URL}/interview/history`,
                {
                    method: "GET",

                    headers: {
                        Authorization:
                            `Bearer ${token}`
                    }
                }
            );


        if (response.status === 401) {

            localStorage.removeItem(
                "token"
            );

            window.location.href =
                "login.html";

            return;
        }


        const history =
            await response.json();
            const inProgressInterview =
    Array.isArray(history)
        ? history.find(item =>
            String(item.status || "").toUpperCase() === "IN_PROGRESS"
        )
        : null;

setupContinueHero(inProgressInterview);


        if (!response.ok) {

            console.error(
                "History error:",
                history
            );

            return;
        }


        historyTable.innerHTML = "";


        if (
            !history ||
            history.length === 0
        ) {

            historyTable.innerHTML = `

                <div class="empty-state">

                    <i class="bi bi-journal-x"></i>

                    <h4>
                        No interviews yet
                    </h4>

                    <p>
                        Start your first mock
                        interview and your results
                        will appear here.
                    </p>

                    <a
                        href="interview-setup.html"
                        class="btn btn-primary"
                    >
                        <i class="bi bi-play-circle-fill"></i>
                        Start Interview
                    </a>

                </div>

            `;

            return;
        }


        /*
         * Put IN_PROGRESS interviews first.
         * This makes the unfinished interview
         * immediately visible.
         */

        const sortedHistory =
            [...history].sort(
                (a, b) => {

                    const aProgress =
                        String(a.status)
                            .toUpperCase()
                            === "IN_PROGRESS";

                    const bProgress =
                        String(b.status)
                            .toUpperCase()
                            === "IN_PROGRESS";


                    if (
                        aProgress &&
                        !bProgress
                    ) {
                        return -1;
                    }


                    if (
                        !aProgress &&
                        bProgress
                    ) {
                        return 1;
                    }


                    return 0;
                }
            );


        sortedHistory.forEach(item => {

            const status =
                String(
                    item.status ||
                    "COMPLETED"
                ).toUpperCase();


            const score =
                item.total_score ?? 0;


            const category =
                item.category ||
                "Interview";


            const isInProgress =
                status === "IN_PROGRESS";


            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "history-card";


            const action =
                isInProgress

                ? `

                    <button
                        type="button"
                        class="continue-interview-btn"
                        data-interview-id="${item.id}"
                    >
                        <i class="bi bi-play-fill"></i>
                        Continue Interview
                    </button>

                  `

                : `

                    <span class="history-completed-label">
                        <i class="bi bi-check-circle-fill"></i>
                        Completed
                    </span>

                  `;


            card.innerHTML = `

                <div class="history-left">

                    <div class="history-icon">

                        <i class="bi bi-mic-fill"></i>

                    </div>


                    <div>

                        <h5>
                            ${escapeHtml(category)}
                        </h5>


                        <span
                            class="history-status ${
                                isInProgress
                                    ? "in-progress"
                                    : "completed"
                            }"
                        >

                            <i class="bi ${
                                isInProgress
                                    ? "bi-clock-fill"
                                    : "bi-check-circle-fill"
                            }"></i>

                            ${
                                isInProgress
                                    ? "IN PROGRESS"
                                    : "COMPLETED"
                            }

                        </span>

                    </div>

                </div>


                <div class="history-right">

                    <strong>
    ${
        isInProgress
            ? "In progress"
            : `${score}%`
    }
</strong>

                    <small>
                        Interview #${item.id}
                    </small>

                    ${action}

                </div>

            `;


            historyTable.appendChild(
                card
            );


            const continueButton =
                card.querySelector(
                    ".continue-interview-btn"
                );


            if (continueButton) {

                continueButton.addEventListener(
                    "click",
                    () => {

                        continueInterview(
                            item.id
                        );

                    }
                );
            }

        });

    }

    catch (error) {

        console.error(
            "Unable to load interview history:",
            error
        );


        historyTable.innerHTML = `

            <div class="empty-state">

                <i class="bi bi-exclamation-circle"></i>

                <h4>
                    Unable to load history
                </h4>

                <p>
                    Please try refreshing the page.
                </p>

            </div>

        `;
    }
}
/* ==========================================================
   HERO CONTINUE INTERVIEW
========================================================== */

function setupContinueHero(interview) {

    const button =
        document.getElementById(
            "continueInterviewBtn"
        );

    if (!button) return;

    if (!interview || !interview.id) {

        button.classList.add("d-none");

        return;
    }

    button.classList.remove("d-none");

    button.onclick = function () {

        continueInterview(
            interview.id
        );

    };
}


/* ==========================================================
   LOGOUT
========================================================== */

function setupLogout() {

    const logoutButton =
        document.querySelector(
            ".logout"
        );

    if (!logoutButton) return;


    logoutButton.addEventListener(
        "click",
        function(event) {

            event.preventDefault();

            localStorage.removeItem(
                "token"
            );

            localStorage.removeItem(
                "currentInterviewId"
            );

            window.location.href =
                "login.html";
        }
    );
}


/* ==========================================================
   START INTERVIEW
========================================================== */

function setupStartInterview() {

    const startButton =
        document.querySelector(
            ".hero-banner a"
        );

    if (!startButton) return;


    startButton.addEventListener(
        "click",
        function() {

            console.log(
                "Opening interview setup..."
            );
        }
    );
}


/* ==========================================================
   HTML ESCAPING
========================================================== */

function escapeHtml(value) {

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}


/* ==========================================================
   INITIALIZE DASHBOARD
========================================================== */

updateGreeting();

updateMotivation();

loadDashboard();

loadHistory();

setupLogout();

setupStartInterview();
