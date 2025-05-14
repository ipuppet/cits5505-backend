function processExerciseData(exercises) {
    const typeStats = {}
    const dailyStats = {}
    const strengthData = []

    exercises.forEach(ex => {
        const date = new Date(ex.created_at).toISOString().split("T")[0]
        const type = formatName(ex.type)

        // Statistics by exercise type
        if (!typeStats[type]) {
            typeStats[type] = {
                distance: 0, duration: 0, totalWeight: 0, sets: 0, reps: 0
            }
        }

        // General metrics processing
        if (ex.metrics.distance) typeStats[type].distance += ex.metrics.distance
        if (ex.metrics.duration) typeStats[type].duration += ex.metrics.duration

        // Strength training specific statistics
        if (ex.type === "WEIGHTLIFTING") {
            const volume = ex.metrics.sets * ex.metrics.reps * ex.metrics.weight
            strengthData.push({
                date, volume, weight: ex.metrics.weight, sets: ex.metrics.sets, reps: ex.metrics.reps
            })
            typeStats[type].totalWeight += ex.metrics.weight
            typeStats[type].sets += ex.metrics.sets
            typeStats[type].reps += ex.metrics.reps
        }

        // Daily activity statistics
        if (!dailyStats[date]) dailyStats[date] = {count: 0, duration: 0}
        dailyStats[date].count++
        dailyStats[date].duration += ex.metrics.duration || 0
    })

    return {
        typeStats: Object.entries(typeStats).map(([type, metrics]) => ({type, ...metrics})),
        dailyStats: Object.entries(dailyStats).map(([date, stats]) => ({date, ...stats})),
        strengthData
    }
}

function createTypeDistributionChart(processedData) {
    const ctx = document.getElementById("typeDistribution")
    const counts = processedData.typeStats.map(t => t.distance ? t.distance / 10 : t.sets)

    if (!counts.length || counts.every(c => c === 0)) {
        ctx.parentElement.innerHTML = "<div class=\"no-data\">No exercise type data available</div>"
        return
    }

    new Chart(ctx, {
        type: "pie", data: {
            labels: processedData.typeStats.map(t => t.type), datasets: [{
                data: counts, backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"], hoverOffset: 4
            }]
        }, options: {
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (ctx) => {
                            const data = processedData.typeStats[ctx.dataIndex]
                            return `${data.type}: ${data.distance ? data.distance + "km" : data.sets + "sets"}`
                        }
                    }
                }
            }
        }
    })
}

function createCardioChart(processedData) {
    const ctx = document.getElementById("cardioChart")
    const cardioData = processedData.typeStats.filter(t => t.distance)

    if (!cardioData.length || cardioData.every(t => t.distance === 0 && t.duration === 0)) {
        ctx.parentElement.innerHTML = "<div class=\"no-data\">No cardio data available</div>"
        return
    }

    new Chart(ctx, {
        type: "bar", data: {
            labels: cardioData.map(t => t.type), datasets: [{
                label: "Total Distance (km)",
                data: cardioData.map(t => t.distance),
                backgroundColor: "rgba(54, 162, 235, 0.7)",
                yAxisID: "y"
            }, {
                label: "Total Duration (min)",
                data: cardioData.map(t => t.duration),
                backgroundColor: "rgba(255, 99, 132, 0.7)",
                yAxisID: "y1"
            }]
        }, options: {
            responsive: true, scales: {
                y: {
                    type: "linear", position: "left", title: {display: true, text: "Distance (km)"}
                }, y1: {
                    type: "linear",
                    position: "right",
                    title: {display: true, text: "Duration (minutes)"},
                    grid: {drawOnChartArea: false}
                }
            }
        }
    })
}

function createStrengthRadar(processedData) {
    const ctx = document.getElementById("strengthRadar")
    const strengthType = processedData.typeStats.find(t => t.type === "Weightlifting")

    if (!strengthType || !processedData.strengthData.length) {
        ctx.parentElement.innerHTML = "<div class=\"no-data\">No strength training data available</div>"
        return
    }

    new Chart(ctx, {
        type: "radar", data: {
            labels: ["Max Weight", "Total Sets", "Total Reps", "Training Volume"], datasets: [{
                label: "Strength Training Data",
                data: [strengthType.totalWeight, strengthType.sets, strengthType.reps, strengthType.sets * strengthType.reps * strengthType.totalWeight],
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderColor: "rgba(75, 192, 192, 1)"
            }]
        }, options: {
            scales: {
                r: {
                    beginAtZero: true, ticks: {
                        callback: (value) => value % 1 === 0 ? value : null
                    }
                }
            }
        }
    })
}

function createDailyTrendChart(processedData) {
    const ctx = document.getElementById("dailyTrend")
    const sortedDaily = processedData.dailyStats.sort((a, b) => new Date(a.date) - new Date(b.date))

    if (!processedData.dailyStats.length || !sortedDaily) {
        ctx.parentElement.innerHTML = "<div class=\"no-data\">No daily activity data available</div>"
        return
    }

    new Chart(ctx, {
        type: "line", data: {
            labels: sortedDaily.map(d => d.date), datasets: [{
                label: "Daily Exercise Count", data: sortedDaily.map(d => d.count), borderColor: "#FF6384", tension: 0.3
            }, {
                label: "Total Duration (minutes)",
                data: sortedDaily.map(d => d.duration),
                borderColor: "#36A2EB",
                tension: 0.3
            }]
        }, options: {
            scales: {
                y: {
                    beginAtZero: true, title: {display: true, text: "Value"}
                }
            }
        }
    })
}

function visualizeExerciseData(rawData) {
    const processed = processExerciseData(rawData.exercises)

    createTypeDistributionChart(processed)
    createCardioChart(processed)
    createStrengthRadar(processed)
    createDailyTrendChart(processed)
}

visualizeExerciseData(SharedData)