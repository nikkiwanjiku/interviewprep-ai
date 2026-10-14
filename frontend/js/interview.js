console.log("Interview page loaded.");

/* ==========================================================
   AUTHENTICATION
========================================================== */

const token = localStorage.getItem("token");
const interviewId = localStorage.getItem("currentInterviewId");

if (!token) {
    window.location.href = "login.html";
}

if (!interviewId) {

    alert("No active interview found.");

    window.location.href = "interview-setup.html";
}


/* ==========================================================
   GLOBAL VARIABLES
========================================================== */

let questions = [];
let currentQuestion = 0;

let savedAnswers = new Map();

let seconds = 0;
let timerInterval = null;


/* ==========================================================
   DOM ELEMENTS
========================================================== */

const questionText =
    document.getElementById("questionText");

const questionCounter =
    document.getElementById("questionNumber");

const questionNumberSmall =
    document.getElementById("questionNumberSmall");

const answerBox =
    document.getElementById("answer");

const wordCount =
    document.getElementById("wordCount");

const charCount =
    document.getElementById("charCount");

const progressFill =
    document.getElementById("progressBar");

const progressPercent =
    document.getElementById("progressPercent");

const timer =
    document.getElementById("timer");

const previousBtn =
    document.getElementById("previousBtn");

const nextBtn =
    document.getElementById("nextBtn");

const logoutBtn =
    document.getElementById("logoutBtn");


/* ==========================================================
   TIMER
========================================================== */

function startTimer() {

    if (timerInterval) {
        clearInterval(timerInterval);
    }

    timerInterval = setInterval(() => {

        seconds++;

        const minutes =
            Math.floor(seconds / 60);

        const secs =
            seconds % 60;

        if (timer) {

            timer.textContent =
                `⏱ ${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;

        }

    }, 1000);
}


/* ==========================================================
   LOAD QUESTIONS
========================================================== */


/* ==========================================================
   LOAD EXISTING INTERVIEW PROGRESS
========================================================== */

async function loadInterviewProgress() {

    try {

        const response = await fetch(
            `${API_URL}/interview/${interviewId}`,
            {
                method: "GET",

                headers: {
                    "Accept": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {

            console.error(
                "Interview progress error:",
                data
            );

            return;
        }

        console.log(
            "Existing interview:",
            data
        );

        savedAnswers = new Map(
            (data.answers || []).map(answer => [
                String(answer.question_id),
                answer
            ])
        );

        console.log(
            `Found ${savedAnswers.size} answered questions.`
        );

        const firstUnansweredIndex =
            questions.findIndex(question =>
                !savedAnswers.has(
                    String(question.id)
                )
            );

        if (firstUnansweredIndex === -1) {

            currentQuestion =
                Math.max(questions.length - 1, 0);

        } else {

            currentQuestion =
                firstUnansweredIndex;
        }

    } catch (error) {

        console.error(
            "Unable to restore interview progress:",
            error
        );

        currentQuestion = 0;
    }
}

async function loadQuestions() {

    try {

        console.log(
            `Loading questions for interview ${interviewId}...`
        );

        const response = await fetch(
            `${API_URL}/interview/${interviewId}/questions`,
            {
                method: "GET",

                headers: {
                    "Accept": "application/json",

                    // IMPORTANT:
                    // Send JWT token to protected endpoint
                    "Authorization": `Bearer ${token}`
                }
            }
        );


        console.log(
            "Questions response status:",
            response.status
        );


        const data = await response.json();


        console.log(
            "Questions response:",
            data
        );


        /* ==================================================
           AUTHENTICATION ERROR
        ================================================== */

        if (response.status === 401) {

            alert(
                "Your session has expired. Please log in again."
            );

            localStorage.removeItem("token");
            localStorage.removeItem("currentInterviewId");

            window.location.href = "login.html";

            return;
        }


        /* ==================================================
           OTHER ERRORS
        ================================================== */

        if (!response.ok) {

            console.error(
                "Question loading error:",
                data
            );

            alert(
                data.detail ||
                "Failed to load interview questions."
            );

            return;
        }


        /* ==================================================
           SAVE QUESTIONS
        ================================================== */

        questions = data;


        if (!Array.isArray(questions)) {

            console.error(
                "Expected questions array but received:",
                questions
            );

            alert(
                "Invalid question data received from server."
            );

            return;
        }


        if (questions.length === 0) {

            alert(
                "No questions were found for this interview."
            );

            return;
        }


        console.log(
            `Loaded ${questions.length} questions.`
        );


        /* ==================================================
           RESTORE INTERVIEW PROGRESS
        ================================================== */

        await loadInterviewProgress();

        startTimer();

        showQuestion();

    } catch (error) {

        console.error(
            "Question loading error:",
            error
        );

        alert(
            "Unable to load interview questions. Please check that the backend is running."
        );
    }
}


/* ==========================================================
   DISPLAY QUESTION
========================================================== */

function showQuestion() {

    if (!questions.length) {
        return;
    }


    const question =
        questions[currentQuestion];


    /* ======================================================
       QUESTION TEXT
    ====================================================== */

    if (questionText) {

        questionText.textContent =
            question.question ||
            question.text ||
            "Question unavailable.";

    }


    /* ======================================================
       QUESTION COUNTER
    ====================================================== */

    if (questionCounter) {

        questionCounter.textContent =
            `Question ${currentQuestion + 1} of ${questions.length}`;

    }

    if (questionNumberSmall) {

        questionNumberSmall.textContent =
            `Q${currentQuestion + 1}`;

    }


    /* ======================================================
       LOAD SAVED ANSWER
    ====================================================== */

    const draft =
        localStorage.getItem(
            `draft-${interviewId}-${currentQuestion}`
        );


    if (answerBox) {

        answerBox.value =
            draft || "";

    }


    /* ======================================================
       UPDATE PROGRESS
    ====================================================== */

    updateProgress();


    /* ======================================================
       UPDATE COUNTERS
    ====================================================== */

    updateCounters();


    /* ======================================================
       BUTTON STATE
    ====================================================== */

    if (previousBtn) {

        previousBtn.disabled =
            currentQuestion === 0;

    }


    if (submitBtn) {

        submitBtn.disabled =
            answerBox ? answerBox.value.trim() === "" : true;

        submitBtn.innerHTML = `
            <i class="bi bi-send-fill"></i>
            <span>Submit Answer</span>
        `;

    }

    if (nextBtn) {

        nextBtn.disabled = true;

        nextBtn.innerHTML =
            currentQuestion === questions.length - 1
                ? `<i class="bi bi-check-circle-fill"></i> Finish Interview`
                : `<i class="bi bi-arrow-right"></i> Next Question`;

    }
}


/* ==========================================================
   UPDATE PROGRESS
========================================================== */

function updateProgress() {

    if (!questions.length) {
        return;
    }


    const percentage =
        ((currentQuestion + 1) /
            questions.length) * 100;


    if (progressFill) {

        progressFill.style.width =
            `${percentage}%`;

    }


    if (progressPercent) {

        progressPercent.textContent =
            `${Math.round(percentage)}%`;

    }
}


/* ==========================================================
   UPDATE WORD / CHARACTER COUNTERS
========================================================== */

function updateCounters() {

    if (!answerBox) {
        return;
    }


    const text =
        answerBox.value.trim();


    const words =
        text.length === 0
            ? 0
            : text.split(/\s+/).length;


    if (wordCount) {

        wordCount.textContent =
            `Words: ${words}`;

    }


    if (charCount) {

        charCount.textContent =
            `Characters: ${answerBox.value.length}`;

    }
}


/* ==========================================================
   AUTO SAVE ANSWER
========================================================== */

if (answerBox) {

    answerBox.addEventListener(
        "input",
        () => {

            localStorage.setItem(

                `draft-${interviewId}-${currentQuestion}`,

                answerBox.value

            );

            updateCounters();

            if (submitBtn) {
                submitBtn.disabled =
                    answerBox.value.trim() === "";
            }

        }
    );

}


/* ==========================================================
   SUBMIT ANSWER
========================================================== */

async function submitAnswer() {

    if (!answerBox) {
        return false;
    }


    const answer =
        answerBox.value.trim();


    if (!answer) {

        alert(
            "Please enter your answer before continuing."
        );

        return false;
    }


    try {

        console.log(
            "Submitting answer for question:",
            questions[currentQuestion].id
        );


        const response = await fetch(

            `${API_URL}/interview/${interviewId}/answer`,

            {
                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json",

                    "Authorization":
                        `Bearer ${token}`

                },

                body: JSON.stringify({

                    question_id:
                        questions[currentQuestion].id,

                    answer:
                        answer

                })
            }
        );


        const data =
            await response.json();


        console.log(
            "Answer submission:",
            data
        );


        /* ==================================================
           AUTH ERROR
        ================================================== */

        if (response.status === 401) {

            alert(
                "Your session has expired. Please log in again."
            );

            localStorage.removeItem("token");
            localStorage.removeItem("currentInterviewId");

            window.location.href =
                "login.html";

            return false;
        }


        /* ==================================================
           OTHER ERRORS
        ================================================== */

        if (!response.ok) {

            console.error(
                "Answer submission error:",
                data
            );

            alert(
                data.detail ||
                "Failed to submit answer."
            );

            return false;
        }


        /* ==================================================
           SAVE FEEDBACK
        ================================================== */

        localStorage.setItem(

            `feedback-${interviewId}-${currentQuestion}`,

            JSON.stringify(data)

        );


        /* ==================================================
           REMOVE DRAFT
        ================================================== */

        localStorage.removeItem(

            `draft-${interviewId}-${currentQuestion}`

        );


        console.log(
            "Answer submitted successfully."
        );

        if (submitBtn) {

            submitBtn.disabled = true;

            submitBtn.innerHTML = `
                <i class="bi bi-check-circle-fill"></i>
                <span>Answer Submitted</span>
            `;

        }

        if (nextBtn) {
            nextBtn.disabled = false;
        }

        savedAnswers.set(
            String(questions[currentQuestion].id),
            data
        );

        return true;


    } catch (error) {

        console.error(
            "Answer submission error:",
            error
        );

        alert(
            "Unable to submit your answer. Please check your connection."
        );

        return false;
    }
}


/* ==========================================================
   NEXT QUESTION
========================================================== */

function nextQuestion() {

    /* ======================================================
       LAST QUESTION
    ====================================================== */

    if (
        currentQuestion ===
        questions.length - 1
    ) {

        finishInterview();

        return;
    }


    /* ======================================================
       MOVE TO NEXT QUESTION
    ====================================================== */

    currentQuestion++;

    showQuestion();
}


/* ==========================================================
   PREVIOUS QUESTION
========================================================== */

function previousQuestion() {

    if (currentQuestion === 0) {
        return;
    }


    currentQuestion--;

    showQuestion();
}


/* ==========================================================
   BUTTON EVENTS
========================================================== */

if (submitBtn) {

    submitBtn.addEventListener(
        "click",
        submitAnswer
    );

}

if (nextBtn) {

    nextBtn.addEventListener(
        "click",
        nextQuestion
    );

}


if (previousBtn) {

    previousBtn.addEventListener(
        "click",
        previousQuestion
    );

}


/* ==========================================================
   FINISH INTERVIEW
========================================================== */

function finishInterview() {

    clearInterval(timerInterval);


    console.log(
        "Interview completed:",
        interviewId
    );


    window.location.href =
        `results.html?id=${interviewId}`;
}


/* ==========================================================
   KEYBOARD SHORTCUT
========================================================== */

if (answerBox) {

    answerBox.addEventListener(
        "keydown",
        (event) => {

            if (
                event.ctrlKey &&
                event.key === "Enter"
            ) {

                nextQuestion();

            }

        }
    );

}


/* ==========================================================
   LOGOUT
========================================================== */

if (logoutBtn) {

    logoutBtn.addEventListener(
        "click",
        (event) => {

            event.preventDefault();

            clearInterval(timerInterval);

            localStorage.removeItem("token");

            localStorage.removeItem(
                "currentInterviewId"
            );

            window.location.href =
                "login.html";

        }
    );

}


/* ==========================================================
   WARN BEFORE LEAVING
========================================================== */

window.addEventListener(
    "beforeunload",
    (event) => {

        if (
            answerBox &&
            answerBox.value.trim() !== ""
        ) {

            event.preventDefault();

            event.returnValue = "";

        }

    }
);


/* ==========================================================
   START APPLICATION
========================================================== */

loadQuestions();