/* ==========================================================
   REGISTER
========================================================== */

const registerForm = document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener("submit", async (e) => {

        e.preventDefault();

        const full_name =
            document.getElementById("full_name").value.trim();

        const email =
            document.getElementById("email").value.trim();

        const password =
            document.getElementById("password").value;

        const career_goal =
            document.getElementById("career_goal").value.trim();


        try {

            const response = await fetch(
                `${API_URL}/auth/register`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        full_name: full_name,
                        email: email,
                        password: password,
                        career_goal: career_goal
                    })
                }
            );


            const data = await response.json();


            /* ==========================================
               REGISTRATION SUCCESS
            ========================================== */

            if (response.ok) {

                alert(
                    "Account created successfully! Please sign in."
                );

                window.location.href = "login.html";

                return;
            }


            /* ==========================================
               REGISTRATION ERROR
            ========================================== */

            alert(
                data.detail || "Registration failed."
            );

        }

        catch (error) {

            console.error(
                "Registration error:",
                error
            );

            alert(
                "Unable to connect to the server."
            );

        }

    });

}


/* ==========================================================
   LOGIN
========================================================== */

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async (e) => {

        e.preventDefault();


        const email =
            document.getElementById("email").value.trim();

        const password =
            document.getElementById("password").value;


        try {

            const response = await fetch(
                `${API_URL}/auth/login`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                }
            );


            const data = await response.json();


            /* ==========================================
               LOGIN SUCCESS
            ========================================== */

            if (response.ok) {

                localStorage.setItem(
                    "token",
                    data.access_token
                );


                alert(
                    "Welcome back! Let's continue your interview practice."
                );


                window.location.href =
                    "dashboard.html";

                return;
            }


            /* ==========================================
               LOGIN ERROR
            ========================================== */

            alert(
                data.detail ||
                "Invalid email or password."
            );

        }

        catch (error) {

            console.error(
                "Login error:",
                error
            );

            alert(
                "Unable to connect to the server."
            );

        }

    });

}