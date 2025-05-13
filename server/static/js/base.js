const navbar = document.querySelector(".navbar")

// Change navbar style on scroll
window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
        navbar.classList.add("scrolled")
    } else {
        navbar.classList.remove("scrolled")
    }
})

function toReadable(str) {
    return str.replace(/([a-z])([A-Z])/g, "$1 $2")
        .replace(/([A-Z]+)([A-Z][a-z])/g, "$1 $2")
        .replace(/_/g, " ")
        .replace(/\b\w/g, char => char.toUpperCase())
}