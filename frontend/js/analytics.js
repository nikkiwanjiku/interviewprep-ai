(() => {
    const token = localStorage.getItem("token");

    if (!token) {
        window.location.href = "login.html";
        return;
    }

    let performanceChart = null;
    let scoreChart = null;

    const completedPercentage = (interview) => {
        const count = Number(interview.question_count) || 0;
        if (count <= 0) return null;

        const score = Number(interview.total_score) || 0;
        return Math.max(0, Math.min(100, score / (count * 10) * 100));
    };

    const formatDate = (value, fallback) => {
        if (!value) return fallback;
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return fallback;

        return date.toLocaleDateString(undefined, {
            month: "short",
            day: "numeric"
        });
    };

    function setText(selector, value) {
        const element = document.querySelector(selector);
        if (element) element.textContent = value;
    }

    function renderCategoryPerformance(interviews) {
        const cards = [...document.querySelectorAll(".analytics-card")];
        const card = cards.find((item) =>
            item.querySelector("h3")?.textContent
                .toLowerCase()
                .includes("performance by category")
        );

        if (!card) return;

        // Preserve the card heading and description, but remove demo bars.
        const heading = card.querySelector("h3");
        const description = card.querySelector("p");
        card.replaceChildren();

        if (heading) card.appendChild(heading);
        if (description) {
            description.textContent = "Based on your completed interview history.";
            card.appendChild(description);
        }

        const list = document.createElement("div");
        list.className = "category-performance-list";

        const groups = new Map();

        for (const interview of interviews) {
            const percentage = completedPercentage(interview);
            if (percentage === null) continue;

            const category = interview.category || "Uncategorised";
            if (!groups.has(category)) {
                groups.set(category, []);
            }
            groups.get(category).push(percentage);
        }

        const entries = [...groups.entries()]
            .map(([category, scores]) => ({
                category,
                average: scores.reduce((sum, score) => sum + score, 0) / scores.length
            }))
            .sort((a, b) => b.average - a.average);

        if (!entries.length) {
            const empty = document.createElement("p");
            empty.textContent = "Complete an interview to see category performance.";
            list.appendChild(empty);
        } else {
            for (const entry of entries) {
                const row = document.createElement("div");
                row.className = "category-performance-row";

                const labels = document.createElement("div");
                labels.className = "category-performance-labels";

                const name = document.createElement("span");
                name.textContent = entry.category;

                const value = document.createElement("strong");
                value.textContent = `${entry.average.toFixed(0)}%`;

                labels.append(name, value);

                const track = document.createElement("div");
                track.className = "category-performance-track";

                const bar = document.createElement("span");
                bar.style.width = `${entry.average}%`;
                track.appendChild(bar);

                row.append(labels, track);
                list.appendChild(row);
            }
        }

        card.appendChild(list);
    }

    function renderCharts(interviews) {
        if (typeof echarts === "undefined") {
            console.warn("ECharts did not load; analytics summary is still available.");
            return;
        }

        const completed = interviews
            .filter(item => String(item.status || "").toUpperCase() === "COMPLETED")
            .map(item => ({
                ...item,
                percentage: completedPercentage(item)
            }))
            .filter(item => item.percentage !== null)
            .sort((a, b) => {
                const dateA = a.completed_at ? new Date(a.completed_at).getTime() : Number(a.id);
                const dateB = b.completed_at ? new Date(b.completed_at).getTime() : Number(b.id);
                return dateA - dateB;
            });

        const trendElement = document.getElementById("performanceChart");
        if (trendElement) {
            performanceChart = echarts.init(trendElement);
            performanceChart.setOption({
                tooltip: { trigger: "axis" },
                grid: { left: 42, right: 20, top: 25, bottom: 35 },
                xAxis: {
                    type: "category",
                    data: completed.map((item, index) =>
                        formatDate(item.completed_at, `#${index + 1}`)
                    ),
                    axisLabel: { color: "#716879" }
                },
                yAxis: {
                    type: "value",
                    min: 0,
                    max: 100,
                    axisLabel: { formatter: "{value}%", color: "#716879" }
                },
                series: [{
                    name: "Score",
                    type: "line",
                    smooth: true,
                    data: completed.map(item => Number(item.percentage.toFixed(1))),
                    areaStyle: { opacity: 0.08 },
                    lineStyle: { width: 3 },
                    symbolSize: 7
                }],
                graphic: completed.length ? [] : [{
                    type: "text",
                    left: "center",
                    top: "middle",
                    style: {
                        text: "Complete an interview to see your trend",
                        fill: "#716879",
                        fontSize: 13
                    }
                }]
            });
        }

        const scoreElement = document.getElementById("scoreChart");
        if (scoreElement) {
            const bins = [
                { name: "Excellent (85–100%)", min: 85, value: 0 },
                { name: "Good (70–84%)", min: 70, max: 85, value: 0 },
                { name: "Needs Work (50–69%)", min: 50, max: 70, value: 0 },
                { name: "Beginner (below 50%)", max: 50, value: 0 }
            ];

            for (const interview of completed) {
                const score = interview.percentage;
                const bin = bins.find(item =>
                    (item.min === undefined || score >= item.min) && (item.max === undefined || score < item.max)
                );
                if (bin) bin.value += 1;
            }

            scoreChart = echarts.init(scoreElement);
            scoreChart.setOption({
                tooltip: { trigger: "item" },
                legend: {
                    bottom: 0,
                    left: "center",
                    textStyle: { color: "#716879" }
                },
                series: [{
                    type: "pie",
                    radius: ["42%", "68%"],
                    center: ["50%", "43%"],
                    data: bins.map(({ name, value }) => ({ name, value })),
                    label: { show: false }
                }]
            });
        }

        window.addEventListener("resize", () => {
            performanceChart?.resize();
            scoreChart?.resize();
        });
    }

    async function loadAnalytics() {
        try {
            const headers = { Authorization: `Bearer ${token}` };

            const [dashboardResponse, historyResponse] = await Promise.all([
                fetch(`${API_URL}/interview/dashboard`, { headers }),
                fetch(`${API_URL}/interview/history`, { headers })
            ]);

            if (dashboardResponse.status === 401 || historyResponse.status === 401) {
                localStorage.removeItem("token");
                window.location.href = "login.html";
                return;
            }

            if (!dashboardResponse.ok || !historyResponse.ok) {
                throw new Error("Unable to retrieve analytics from the server.");
            }

            const dashboard = await dashboardResponse.json();
            const history = await historyResponse.json();

            const stats = [...document.querySelectorAll(".analytics-stat")];

            if (stats[0]?.querySelector("h2")) {
                stats[0].querySelector("h2").textContent =
                    `${Number(dashboard.average_score || 0).toFixed(1)}%`;
            }

            if (stats[1]?.querySelector("h2")) {
                stats[1].querySelector("h2").textContent =
                    dashboard.completed_interviews ?? 0;
            }

            if (stats[2]?.querySelector("h2")) {
                stats[2].querySelector("h2").textContent =
                    `${dashboard.highest_score ?? 0}%`;
            }

            if (stats[0]?.querySelector(".stat-change")) {
                stats[0].querySelector(".stat-change").textContent =
                    dashboard.completed_interviews
                        ? "Average of completed interviews"
                        : "Complete an interview to see your average";
            }

            if (stats[2]?.querySelector(".stat-change")) {
                stats[2].querySelector(".stat-change").textContent =
                    dashboard.completed_interviews
                        ? "Highest completed-interview score"
                        : "Your best score will appear here";
            }

            const completed = Array.isArray(history) ? history : [];
            const finished = completed.filter(
                item => String(item.status || "").toUpperCase() === "COMPLETED"
            );

            renderCategoryPerformance(finished);
            renderCharts(completed);
        } catch (error) {
            console.error("Analytics loading failed:", error);
            setText(".page-subtitle", "Unable to load analytics. Please refresh and try again.");
        }
    }

    document.querySelector("a.logout")?.addEventListener("click", () => {
        localStorage.removeItem("token");
        localStorage.removeItem("currentInterviewId");
        window.location.href = "login.html";
    });

    loadAnalytics();
})();
