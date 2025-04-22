document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search)
    const dropdownParam = urlParams.get("login")
    if (dropdownParam === "true") {
        toggleLogin()
    }

    const toggleLoginLink = document.getElementById("toggleLoginBtn")
    if (toggleLoginLink) {
        toggleLoginLink.addEventListener("click", function (event) {
            event.preventDefault()
            event.stopPropagation()
            toggleLogin()
        })
    }
})

function toggleLogin() {
    const dropdownElement = document.querySelector("#login")
    if (dropdownElement) {
        const dropdown = bootstrap.Dropdown.getOrCreateInstance(dropdownElement)
        dropdown.toggle()
    }
}

function toRegister() {
    window.location.href = "/user/register"
}

function toDashboard() {
    window.location.href = "/dashboard"
}