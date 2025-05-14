function updateGoalProgressBar() {
    CurrentUser.goals.forEach(goal => {
        const percent = Math.min(100, Math.round((goal.current / goal.target) * 100))
        const ctx = document.getElementById(`goal-progress-${goal.id}`)
        if (ctx) {
            new Chart(ctx, {
                type: "doughnut",
                data: {
                    datasets: [{
                        data: [percent, 100 - percent],
                        backgroundColor: [
                            percent >= 100 ? "#28a745" : "#007bff",
                            "#e9ecef"
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    cutout: "70%",
                    plugins: {
                        legend: {display: false},
                        tooltip: {enabled: false}
                    }
                }
            })
        }
    })
}

function initGoalModal() {
    const addGoalModal = document.getElementById("addGoalModal")
    if (!addGoalModal) return
    addGoalModal.addEventListener("shown.bs.modal", function () {
        const exerciseType = addGoalModal.querySelector("[name=\"exercise_type\"]")
        const metric = addGoalModal.querySelector("[name=\"metric\"]")
        const unit = addGoalModal.querySelector("[name=\"unit\"]")

        function getUnit(metric) {
            switch (metric) {
                case "distance":
                    return "m"
                case "duration":
                    return "min"
                case "weight":
                    return "kg"
                default:
                    return ""
            }
        }

        function updateMetricAndUnit() {
            const metrics = MetricsByType[exerciseType.value] || []
            metric.innerHTML = ""
            metrics.forEach(function (m) {
                const opt = document.createElement("option")
                opt.value = m
                opt.textContent = m.charAt(0).toUpperCase() + m.slice(1)
                metric.appendChild(opt)
            })
            if (metrics.length > 0) {
                unit.value = getUnit(metrics[0])
            } else {
                unit.value = ""
            }
        }

        if (exerciseType && metric && unit) {
            exerciseType.addEventListener("change", updateMetricAndUnit)
            metric.addEventListener("change", function () {
                const metrics = MetricsByType[exerciseType.value] || []
                const selected = metrics.find(m => m === this.value)
                if (selected) {
                    unit.value = getUnit(selected)
                }
            })
            // Run on modal open
            updateMetricAndUnit()
        }
    })
}

initGoalModal()
updateGoalProgressBar()
