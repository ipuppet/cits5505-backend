/**
 * Update the exercise metrics based on the selected type.
 */
function exerciseTypeChange() {
    const container = document.querySelector("#exerciseFormContainer")
    container.innerHTML = ""
    const selectedType = document.querySelector("#exerciseForm").type.value
    const selectedMetrics = ExercisesMetrics[selectedType]
    for (const metric of selectedMetrics) {
        const div = document.createElement("div")
        div.className = "mb-3"
        const label = document.createElement("label")
        label.className = "form-label"
        let unitText = ""
        if (metric === "distance") {
            unitText = "(m)"
        } else if (metric === "duration") {
            unitText = "(min)"
        } else if (metric === "weight") {
            unitText = "(kg)"
        }
        label.textContent = `${formatName(metric)} ${unitText}`
        div.appendChild(label)
        const input = document.createElement("input")
        input.className = "form-control"
        input.name = metric
        div.appendChild(input)
        container.appendChild(div)
    }
}

function exerciseSubmit() {
    const form = document.querySelector("#exerciseForm")
    const type = form.type.value
    const metrics = ExercisesMetrics[type]
    const data = {}
    for (const metric of metrics) {
        data[metric] = Number(form[metric].value)
    }
    form.metrics.value = JSON.stringify(data)
}

/**
 * Update the body measurement unit select options based on the selected type.
 */
function bodyMeasurementTypeChange() {
    const selectedType = document.querySelector("#bodyMeasurementForm").type.value
    const selectedUnit = BodyMeasurementUnits[selectedType]
    const unitSelect = document.querySelector("#bodyMeasurementForm").unit
    unitSelect.innerHTML = ""
    for (const unit of selectedUnit) {
        const option = document.createElement("option")
        option.value = unit
        option.textContent = unit
        unitSelect.appendChild(option)
    }
}

function bodyMeasurementSubmit() {
    const form = document.querySelector("#bodyMeasurementForm")
    const type = form.type.value
    const value = form.value.value
    const unit = form.unit.value
    switch (type) {
        case "WEIGHT":
            form.value.value = unit === "kg" ? value : value * 0.453592
            break
        case "HEIGHT":
            form.value.value = unit === "cm" ? value : value * 2.54
            break
    }
}

function calorieIntakeSubmit() {
    const form = document.querySelector("#calorieIntakeForm")
    const unit = form.unit.value
    if (unit === "kJ") {
        // Convert the value to kcal
        const calories = form.calories.value
        form.calories.value = calories * 0.239006
    }
}

const ExerciseModalModal = new bootstrap.Modal("#exerciseModal")
const CalorieIntakeModal = new bootstrap.Modal("#calorieIntakeModal")
const BodyMeasurementModal = new bootstrap.Modal("#bodyMeasurementModal")

function showModal() {
    const dataType = document.querySelector("#dataTypeSelect").value
    const datasetType = document.querySelector("input[name=\"dataset\"]:checked").id
    if (datasetType === "browseBodyMeasurement") {
        const form = document.querySelector("#bodyMeasurementForm")
        form.type.value = dataType
        bodyMeasurementTypeChange()
        BodyMeasurementModal.show()
    } else if (datasetType === "browseCalorieIntake") {
        CalorieIntakeModal.show()
    } else if (datasetType === "browseExercise") {
        const form = document.querySelector("#exerciseForm")
        form.type.value = dataType
        exerciseTypeChange()
        ExerciseModalModal.show()
    }
}