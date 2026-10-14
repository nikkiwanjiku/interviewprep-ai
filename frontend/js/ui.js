/* ==========================================================
   AKIRA UI UTILITIES
========================================================== */

/* ==========================================
   TOAST
========================================== */

function showToast(message, type = "success") {

    const toast = document.createElement("div");

    toast.className = `toast toast-${type}`;

    toast.innerHTML = `
        <span>${message}</span>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("show");
    }, 50);

    setTimeout(() => {

        toast.classList.remove("show");

        setTimeout(() => {

            toast.remove();

        }, 300);

    }, 3000);

}

/* ==========================================
   LOADING OVERLAY
========================================== */

function showLoader(message = "Loading...") {

    if (document.getElementById("loadingOverlay")) return;

    const overlay = document.createElement("div");

    overlay.id = "loadingOverlay";

    overlay.innerHTML = `

        <div class="loading-content">

            <div class="loader"></div>

            <p>${message}</p>

        </div>

    `;

    document.body.appendChild(overlay);

}

function hideLoader() {

    const overlay = document.getElementById("loadingOverlay");

    if (overlay) {

        overlay.remove();

    }

}

/* ==========================================
   CONFIRM DIALOG
========================================== */

function confirmAction(message) {

    return window.confirm(message);

}

/* ==========================================
   FORMAT SCORE
========================================== */

function formatScore(score) {

    return `${score}%`;

}

/* ==========================================
   INITIALS
========================================== */

function getInitials(name) {

    if (!name) return "";

    return name
        .split(" ")
        .map(word => word[0])
        .join("")
        .toUpperCase();

}