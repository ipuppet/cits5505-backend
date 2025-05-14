function fetchWaterAmount() {
    fetch("/dashboard/water?now=" + new Date().toISOString())
        .then(res => {
            if (!res.ok) {
                throw new Error("Network response was not ok")
            }
            return res.json()
        })
        .then(data => updateWaterUI(data.data))
        .catch(err => {
            console.error("Error fetching water amount:", err)
            const msgEl = document.getElementById("hydration-progress-message")
            if (msgEl) msgEl.textContent = "Error fetching hydration data. Please try again later."
        })
}

function addWater(ml) {
    fetch("/dashboard/water", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({amount: ml})
    }).then(fetchWaterAmount)
}

function undoLastWater() {
    fetch("/dashboard/water", {
        method: "DELETE",
        headers: {"Content-Type": "application/json"}
    }).then(fetchWaterAmount)
}

function updateWaterUI(amount) {
    const goal = 2000
    document.getElementById("water-amount").textContent = amount
    document.getElementById("water-goal").textContent = goal
    const percent = Math.min(100, (amount / goal) * 100)
    const bar = document.getElementById("water-progress")
    bar.style.width = percent + "%"
    bar.setAttribute("aria-valuenow", amount)

    // Fun motivational messages
    const msgEl = document.getElementById("hydration-progress-message")
    let msg = ""
    if (amount === 0) msg = "Start your day with a glass of water! 💦"
    else if (percent < 50) msg = "Keep going! Your body thanks you. 🚰"
    else if (percent < 100) msg = "Almost there! Just a bit more to go! 🏃‍♂️"
    else msg = "Awesome! You've hit your hydration goal! 🎉"
    if (msgEl) msgEl.textContent = msg
}

fetchWaterAmount()