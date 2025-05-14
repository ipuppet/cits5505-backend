function getLast14DaysLabels() {
    const labels = []
    const today = new Date()
    for (let i = 13; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(today.getDate() - i)
        const label = date.toLocaleDateString()
        labels.push(label)
    }
    return labels
}

const UserWeightByDate = Object.fromEntries(getLast14DaysLabels().map(key => [key, null]))
CurrentUser.bodyMeasurements.forEach(measurement => {
    if (measurement.type !== "WEIGHT") return
    const date = new Date(measurement.created_at).toLocaleDateString()
    if (UserWeightByDate[date] === null) {
        UserWeightByDate[date] = measurement.value
    }
})
const UserCalorieIntakeByDate = {}
CurrentUser.calorieIntakes.forEach(intake => {
    const date = new Date(intake.created_at).toLocaleDateString()
    if (!UserCalorieIntakeByDate[date]) {
        UserCalorieIntakeByDate[date] = 0
    }
    UserCalorieIntakeByDate[date] += intake.calories
})

new Chart(document.getElementById("exerciseChart"), {
    type: "bar",
    data: {
        labels: Object.keys(CurrentUser.calorieBurned).map(date => new Date(date).toLocaleDateString()),
        datasets: [{
            label: "Calories Burned",
            data: Object.values(CurrentUser.calorieBurned),
            backgroundColor: "rgba(75, 192, 192, 0.6)",
            borderColor: "rgba(75, 192, 192, 1)",
            borderWidth: 1
        }]
    },
    options: {responsive: true, scales: {y: {beginAtZero: true}}}
})
new Chart(document.getElementById("intakeChart"), {
    type: "bar",
    data: {
        labels: Object.keys(UserCalorieIntakeByDate),
        datasets: [{
            label: "Calories Intake",
            data: Object.values(UserCalorieIntakeByDate),
            backgroundColor: "rgba(255, 159, 64, 0.6)",
            borderColor: "rgba(255, 159, 64, 1)",
            borderWidth: 1
        }]
    },
    options: {responsive: true, scales: {y: {beginAtZero: true}}}
})
new Chart(document.getElementById("weightChart"), {
    type: "line",
    data: {
        labels: Object.keys(UserWeightByDate),
        datasets: [{
            label: "Weight (kg)",
            data: Object.values(UserWeightByDate),
            backgroundColor: "rgba(54, 162, 235, 0.2)",
            borderColor: "rgba(54, 162, 235, 1)",
            fill: false,
            tension: 0.3,
            pointRadius: 5,
            pointBackgroundColor: "rgba(54, 162, 235, 1)"
        }]
    },
    options: {
        responsive: true,
        scales: {y: {beginAtZero: false, title: {display: true, text: "kg"}}},
        spanGaps: true // <-- Move spanGaps here
    }

})