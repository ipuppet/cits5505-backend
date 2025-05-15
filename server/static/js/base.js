const navbar = document.querySelector(".navbar")

// Change navbar style on scroll
window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
        navbar.classList.add("scrolled")
    } else {
        navbar.classList.remove("scrolled")
    }
})

function formatName(name) {
    return name
        .split("_")
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(" ")
}

function getUnit(metric) {
    if (metric === "distance") {
        return "m"
    } else if (metric === "duration") {
        return "min"
    } else if (metric === "weight") {
        return "kg"
    }
    return null
}

// Add timezone conversion function, consistent with browse page
function convertTimezone(data, key = "created_at") {
    if (!Array.isArray(data)) return data

    const result = JSON.parse(JSON.stringify(data)) // Deep copy of the array
    for (let i = 0; i < result.length; i++) {
        if (result[i][key]) {
            const date = new Date(result[i][key])
            result[i][key] = date.toLocaleString()
        }
    }
    return result
}

// Set the default timezone in the select element
const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone
document.querySelectorAll("select[name=\"timezone\"]").forEach(select => {
    const option = Array.from(select.options).find(opt =>
        opt.value === browserTimezone ||
        opt.text.includes(browserTimezone)
    )
    if (option) option.selected = true
})
// Set max date to today
const today = new Date().toLocaleDateString("en-CA")
document.querySelectorAll("input[type=\"date\"]").forEach(input => {
    input.setAttribute("max", today)
})
