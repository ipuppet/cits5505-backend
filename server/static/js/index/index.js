document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search)
    const dropdownParam = urlParams.get("login")
    if (dropdownParam === "true") {
        toggleLogin()
    }
})

function toggleLogin() {
    const dropdownElement = document.querySelector("#login")
    if (dropdownElement) {
        const dropdown = new bootstrap.Dropdown(dropdownElement)
        dropdown.toggle()
    }
}

function toRegister() {
    window.location.href = "/user/register"
}

function toDashboard() {
    window.location.href = "/dashboard"
}