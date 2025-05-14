// Example: Use the first day in weather_forecast for today's weather
let suggestion = "Stay active!"
if (Weather && Weather.length > 0) {
    const today = Weather[0]
    const desc = today.description.toLowerCase()
    if (desc.includes("rain") || desc.includes("storm")) {
        suggestion = "It's wet outside. Try an indoor workout like yoga or bodyweight exercises!"
    } else if (desc.includes("clear") || desc.includes("sunny")) {
        suggestion = "Great weather! Go for a run, walk, or cycle outdoors."
    } else if (desc.includes("cloud")) {
        suggestion = "Mild weather. A brisk walk or outdoor stretching is perfect!"
    } else if (desc.includes("snow")) {
        suggestion = "Snowy day! Consider an indoor HIIT or dance workout."
    } else {
        suggestion = "Check the weather and choose your favorite activity!"
    }
}
const el = document.getElementById("weather-workout-suggestion")
if (el) {
    el.innerHTML = `
        <div style="font-size:1.2em;">
            <span style="font-size:2em;">💡</span>
            <strong>${suggestion}</strong>
        </div>
        <div class="mt-2 text-muted" style="font-size:0.95em;">
            Weather: ${Weather && Weather.length > 0 ? Weather[0].description : "N/A"},
            Temp: ${Weather && Weather.length > 0 ? Weather[0].temp + "°C" : "N/A"}
        </div>
    `
}