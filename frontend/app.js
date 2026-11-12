
const API_BASE_URL = "http://127.0.0.1:8001";

const form = document.getElementById("evaluation-form");
const results = document.getElementById("results");
const historyContainer = document.getElementById("history");

// Safely create text elements
function createTextElement(tag, text, className = "") {
    const element = document.createElement(tag);
    element.textContent = text;

    if (className) {
        element.className = className;
    }

    return element;
}

// Display evaluation results
function displayResults(data) {
    results.replaceChildren();

    results.appendChild(
        createTextElement("h2", "Evaluation Results")
    );

    // Visual score indicator
    const scoreIndicator = document.createElement("div");
    scoreIndicator.className = "score-indicator";

    const scoreCircle = document.createElement("div");
    scoreCircle.className = "score-circle";

    const scoreValue = document.createElement("span");
    scoreValue.textContent = `${data.score}`;

    const percentage = Math.max(
        0,
        Math.min(100, (data.score / data.max_score) * 100)
    );

    scoreCircle.style.setProperty("--score", `${percentage}%`);
    scoreCircle.appendChild(scoreValue);

    const scoreInfo = document.createElement("div");
    scoreInfo.className = "score-info";

    scoreInfo.appendChild(
        createTextElement("h3", `${data.score} / ${data.max_score}`)
    );

    scoreInfo.appendChild(
        createTextElement("p", `Grade: ${data.grade}`)
    );

    scoreIndicator.appendChild(scoreCircle);
    scoreIndicator.appendChild(scoreInfo);

    results.appendChild(scoreIndicator);

    // Criterion scores
    const criteria = document.createElement("div");

    for (const [name, score] of Object.entries(data.criterion_scores)) {
        criteria.appendChild(
            createTextElement(
                "p",
                `${name.charAt(0).toUpperCase() + name.slice(1)}: ${score}/5`
            )
        );
    }

    results.appendChild(criteria);

    // AI-generated explanations
    if (data.explanations) {
        results.appendChild(
            createTextElement("h3", "AI Evaluation Explanations")
        );

        const explanationLabels = {
            accuracy: "Accuracy",
            relevance: "Relevance",
            completeness: "Completeness",
            clarity: "Clarity",
        };

        const explanationContainer = document.createElement("div");
        explanationContainer.className = "explanation-container";

        for (const [key, label] of Object.entries(explanationLabels)) {
            const section = document.createElement("div");
            section.className = "explanation-item";

            section.appendChild(
                createTextElement("h4", label)
            );

            section.appendChild(
                createTextElement(
                    "p",
                    data.explanations[key] || "No explanation available."
                )
            );

            explanationContainer.appendChild(section);
        }

        results.appendChild(explanationContainer);
    }
}

// Submit evaluation to FastAPI
form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const mode = document.getElementById("evaluation-mode").value;

    const payload = {
        prompt: document.getElementById("prompt").value.trim(),
        response: document.getElementById("response").value.trim(),
    };

    // Include manual ratings only in manual mode
    if (mode === "manual") {
        payload.accuracy = Number(document.getElementById("accuracy").value);
        payload.relevance = Number(document.getElementById("relevance").value);
        payload.completeness = Number(document.getElementById("completeness").value);
        payload.clarity = Number(document.getElementById("clarity").value);
    }

    const endpoint = mode === "automatic"
        ? "/evaluations/auto"
        : "/evaluations/score";

    const button = form.querySelector("button[type='submit']");
    button.disabled = true;
    button.textContent = mode === "automatic"
        ? "AI Evaluating..."
        : "Evaluating...";

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                errorData.detail || `API error: ${response.status}`
            );
        }

        const data = await response.json();

        displayResults(data);

        // Refresh history and analytics
        await loadHistory();
        await loadAnalytics();

    } catch (error) {
        results.replaceChildren(
            createTextElement("h2", "Evaluation Results"),
            createTextElement("p", error.message)
        );
    } finally {
        button.disabled = false;
        button.textContent = "Evaluate Response";
    }
});

// Load previous evaluations
async function loadHistory() {
    try {
        const grade = document.getElementById("grade-filter").value;

        const params = new URLSearchParams({
            limit: "10",
            offset: "0",
        });

        if (grade) {
            params.set("grade", grade);
        }

        const response = await fetch(
            `${API_BASE_URL}/evaluations?${params.toString()}`
        );

        if (!response.ok) {
            throw new Error("Could not load evaluation history.");
        }

        const data = await response.json();

        historyContainer.replaceChildren();

        if (data.results.length === 0) {
            historyContainer.appendChild(
                createTextElement("p", "No evaluations yet.")
            );
            return;
        }

        const table = document.createElement("table");
        const header = document.createElement("tr");

        ["ID", "Prompt", "Score", "Grade", "Date"].forEach((heading) => {
            header.appendChild(createTextElement("th", heading));
        });

        table.appendChild(header);

        data.results.forEach((item) => {
            const row = document.createElement("tr");

            const date = item.created_at
                ? new Date(item.created_at).toLocaleDateString()
                : "N/A";

            [
                item.id,
                item.prompt,
                `${item.score}/${item.max_score}`,
                item.grade,
                date,
            ].forEach((value) => {
                row.appendChild(createTextElement("td", String(value)));
            });

            // Make each history row clickable
                row.style.cursor = "pointer";
                row.title = "Click to view evaluation details";

                row.addEventListener("click", () => {
                    loadEvaluationDetails(item.id);
                });

            table.appendChild(row);
        });

        historyContainer.appendChild(table);

    } catch (error) {
        historyContainer.replaceChildren(
            createTextElement("p", error.message)
        );
    }
}

// Load history when the page opens
loadHistory();

// Load dashboard analytics from FastAPI
async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics`);

        if (!response.ok) {
            throw new Error("Could not load analytics.");
        }

        const data = await response.json();

        document.getElementById("total-evaluations").textContent =
            data.total_evaluations;

        document.getElementById("average-score").textContent =
            `${data.average_score}/100`;

        document.getElementById("excellent-count").textContent =
            data.grade_counts["Excellent"];

        document.getElementById("good-count").textContent =
            data.grade_counts["Good"];

        document.getElementById("fair-count").textContent =
            data.grade_counts["Fair"];

        document.getElementById("poor-count").textContent =
            data.grade_counts["Poor"] +
            data.grade_counts["Very Poor"];
            // Calculate excellent and non-excellent percentages
            const excellentCount = data.grade_counts["Excellent"];
            const totalEvaluations = data.total_evaluations;

            const excellentRate = totalEvaluations > 0
                ? (excellentCount / totalEvaluations) * 100
                : 0;

            const otherRate = totalEvaluations > 0
                ? 100 - excellentRate
                : 0;

            // Display percentages
            document.getElementById("excellent-rate").textContent =
                `${excellentRate.toFixed(1)}%`;

            document.getElementById("other-rate").textContent =
                `${otherRate.toFixed(1)}%`;

            // Update average score progress bar
            document.getElementById("average-score-bar").style.width =
                `${Math.max(0, Math.min(100, data.average_score))}%`;

            // Render grade distribution chart
            const gradeChart = document.getElementById("grade-chart");

            gradeChart.replaceChildren();

            const grades = [
                { name: "Excellent", color: "#a78bfa" },
                { name: "Good", color: "#60a5fa" },
                { name: "Fair", color: "#fbbf24" },
                { name: "Poor", color: "#fb923c" },
                { name: "Very Poor", color: "#f87171" },
            ];

            const maxCount = Math.max(
                1,
                ...grades.map(grade => data.grade_counts[grade.name] || 0)
            );

            grades.forEach((grade) => {
                const count = data.grade_counts[grade.name] || 0;
                const percentage = (count / maxCount) * 100;

                const row = document.createElement("div");
                row.className = "grade-chart-row";

                const label = createTextElement("span", grade.name);
                label.className = "grade-chart-label";

                const track = document.createElement("div");
                track.className = "grade-chart-track";

                const fill = document.createElement("div");
                fill.className = "grade-chart-fill";
                fill.style.width = `${percentage}%`;
                fill.style.backgroundColor = grade.color;

                track.appendChild(fill);

                const value = createTextElement("span", String(count));
                value.className = "grade-chart-value";

                row.append(label, track, value);
                gradeChart.appendChild(row);
            });
        } 
    
    catch (error) {
        console.error("Analytics error:", error);

        document.querySelectorAll(".analytics-card p").forEach((card) => {
            card.textContent = "Unavailable";
        });
    }
}
// Update history when the grade filter changes
document.getElementById("grade-filter").addEventListener("change", () => {
    loadHistory();
});

// Load analytics when the dashboard opens
loadHistory();
loadAnalytics();
loadEvaluationTrends();

// Load and display details for a selected evaluation
async function loadEvaluationDetails(evaluationId) {
    const detailSection = document.getElementById("evaluation-detail");
    const detailContent = document.getElementById("detail-content");

    detailSection.hidden = false;
    detailContent.replaceChildren(
        createTextElement("p", "Loading evaluation details...")
    );

    try {
        const response = await fetch(
            `${API_BASE_URL}/evaluations/${evaluationId}`
        );

        if (!response.ok) {
            throw new Error("Could not load evaluation details.");
        }

        const data = await response.json();

        detailContent.replaceChildren();

        detailContent.appendChild(
            createTextElement("h3", `Evaluation #${data.id}`)
        );

        detailContent.appendChild(
            createTextElement("p", `Prompt: ${data.prompt}`)
        );

        detailContent.appendChild(
            createTextElement("p", `AI Response: ${data.response}`)
        );

        detailContent.appendChild(
            createTextElement("h3", `Score: ${data.score}/${data.max_score}`)
        );

        detailContent.appendChild(
            createTextElement("p", `Grade: ${data.grade}`)
        );

        const criteria = [
            ["Accuracy", data.accuracy],
            ["Relevance", data.relevance],
            ["Completeness", data.completeness],
            ["Clarity", data.clarity],
        ];

        criteria.forEach(([name, score]) => {
            detailContent.appendChild(
                createTextElement("p", `${name}: ${score}/5`)
            );
        });

        detailContent.appendChild(
            createTextElement(
                "p",
                `Created: ${new Date(data.created_at).toLocaleString()}`
            )
        );
        // Display AI-generated explanations
        if (data.explanations) {
            const explanationHeading = createTextElement(
                "h3",
                "AI Evaluation Explanations"
            );

            detailContent.appendChild(explanationHeading);

            const explanationContainer = document.createElement("div");
            explanationContainer.className = "explanation-container";

            const explanationItems = [
                ["Accuracy", data.explanations.accuracy],
                ["Relevance", data.explanations.relevance],
                ["Completeness", data.explanations.completeness],
                ["Clarity", data.explanations.clarity],
            ];

            explanationItems.forEach(([name, explanation]) => {
                const item = document.createElement("div");
                item.className = "explanation-item";

                item.appendChild(createTextElement("h4", name));
                item.appendChild(createTextElement("p", explanation));

                explanationContainer.appendChild(item);
            });

            detailContent.appendChild(explanationContainer);
        }
        detailSection.scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        detailContent.replaceChildren(
            createTextElement("p", error.message)
        );
    }
}

// Close evaluation details
document.getElementById("close-detail").addEventListener("click", () => {
    document.getElementById("evaluation-detail").hidden = true;
});

const evaluationMode = document.getElementById("evaluation-mode");
const manualCriteria = document.getElementById("manual-criteria");

function updateEvaluationMode() {
    manualCriteria.hidden = evaluationMode.value === "automatic";
}

evaluationMode.addEventListener("change", updateEvaluationMode);

updateEvaluationMode();

async function loadEvaluationTrends() {
    const trendChart = document.getElementById("trend-chart");

    try {
        const response = await fetch(
            `${API_BASE_URL}/analytics/trends`
        );

        if (!response.ok) {
            throw new Error("Could not load evaluation trends.");
        }

        const data = await response.json();

        trendChart.replaceChildren();

        if (data.dates.length === 0) {
            trendChart.appendChild(
                createTextElement("p", "No evaluation trends available yet.")
            );
            return;
        }

        const chart = document.createElement("div");
        chart.className = "trend-chart-list";

        data.dates.forEach((date, index) => {
            const row = document.createElement("div");
            row.className = "trend-chart-row";

            const label = createTextElement(
                "span",
                new Date(`${date}T00:00:00`).toLocaleDateString()
            );
            label.className = "trend-date";

            const track = document.createElement("div");
            track.className = "trend-track";

            const fill = document.createElement("div");
            fill.className = "trend-fill";
            fill.style.width =
                `${Math.max(0, Math.min(100, data.average_scores[index]))}%`;

            track.appendChild(fill);

            const value = createTextElement(
                "span",
                `${data.average_scores[index].toFixed(2)}`
            );
            value.className = "trend-value";

            const count = createTextElement(
                "small",
                `${data.evaluation_counts[index]} evaluations`
            );
            count.className = "trend-count";

            row.append(label, track, value, count);
            chart.appendChild(row);
        });

        trendChart.appendChild(chart);

    } catch (error) {
        console.error("Trend chart error:", error);

        trendChart.replaceChildren(
            createTextElement("p", "Unable to load performance trends.")
        );
    }
}
