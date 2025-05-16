document.getElementById("avatar").addEventListener("change", function () {
    if (this.files.length > 0) {
        document.getElementById("avatar-form").submit()
    }
})


function renderMotivationMessage() {
    const messages = [
        "You’re one step closer to your goals!",
        "Keep pushing, your future self will thank you!",
        "Every workout counts. Stay strong!",
        "Consistency is key. You’ve got this!",
        "Small steps lead to big changes!",
        "Believe in yourself and all that you are.",
        "Your only limit is you. Go for it!",
        "Sweat now, shine later!",
        "Progress, not perfection!"
    ]
    const msg = messages[Math.floor(Math.random() * messages.length)]
    const el = document.getElementById("motivation-message")
    if (el) el.textContent = msg
}

function renderUserInfo() {
    const greetingLine = document.getElementById("greeting-line")
    if (greetingLine) {
        const hour = new Date().getHours()
        let greeting = "Hello"
        let emoji = "👋"
        if (hour >= 5 && hour < 12) {
            greeting = "Good morning"
            emoji = "🌅"
        } else if (hour >= 12 && hour < 18) {
            greeting = "Good afternoon"
            emoji = "☀️"
        } else if (hour >= 18 && hour < 22) {
            greeting = "Good evening"
            emoji = "🌇"
        } else {
            greeting = "Good night"
            emoji = "🌙"
        }
        greetingLine.innerHTML = `<span>${emoji} ${greeting}, <strong>${CurrentUser.nickname}</strong></span>`
    }

    // format date
    const lastLogin = new Date(CurrentUser.lastLogin)
    const today = new Date()
    let lastLoginString
    if (lastLogin.getDate() === today.getDate() && lastLogin.getMonth() === today.getMonth() && lastLogin.getFullYear() === today.getFullYear()) {
        lastLoginString = "Today, " + lastLogin.toLocaleTimeString([], {
            hour: "2-digit", minute: "2-digit", timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
        })
    } else {
        lastLoginString = lastLogin.toLocaleString([], {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
        })
    }
    document.getElementById("lastLogin").textContent = lastLoginString

    const createdAt = new Date(CurrentUser.createdAt)
    document.getElementById("createdAt").textContent = createdAt.toLocaleDateString()
}

renderMotivationMessage()
renderUserInfo()
