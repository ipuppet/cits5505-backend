const bmiBar = document.getElementById("bmiBar")
const ctx = bmiBar.getContext("2d")
// Draw colored ranges
const ranges = [
    {min: 15, max: 18.5, color: "#4fc3f7"}, // Underweight
    {min: 18.5, max: 25, color: "#81c784"}, // Normal
    {min: 25, max: 30, color: "#ffe066"},   // Overweight
    {min: 30, max: 40, color: "#ffb74d"}    // Obesity
]
const width = bmiBar.width, height = bmiBar.height
ranges.forEach(r => {
    const x1 = ((r.min - 15) / 25) * width
    const x2 = ((r.max - 15) / 25) * width
    ctx.fillStyle = r.color
    ctx.fillRect(x1, 0, x2 - x1, height)
})
// Draw pointer for user's BMI if available and in range
if (BMI !== null && !isNaN(BMI) && BMI >= 15 && BMI <= 40) {
    const x = ((BMI - 15) / 25) * width
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x - 7, height)
    ctx.lineTo(x + 7, height)
    ctx.closePath()
    ctx.fillStyle = "#f44336"
    ctx.fill()
}