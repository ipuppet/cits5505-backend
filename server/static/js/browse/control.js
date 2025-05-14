function createDataset(datasetType, visualType) {
    const dataset = {}
    if (datasetType === "browseExercise") {
        if (visualType === "tableButton") {
            dataset.headers = type => (ExercisesMetrics[type] || []).concat(["created_at"])
        } else {
            dataset.headers = type => ExercisesMetrics[type]
        }
        dataset.data = type => UserExercises
            .filter(exercise => exercise.type === type)
            .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
            .map(
                exercise => ({
                    ...exercise.metrics,
                    created_at: new Date(exercise.created_at).toLocaleString()
                })
            )

    } else if (datasetType === "browseCalorieIntake") {
        if (visualType === "tableButton") {
            dataset.headers = type => ["calories", "description", "created_at"]
        } else {
            dataset.headers = type => ["calories"]
        }
        dataset.data = () => UserCalorieIntakes
            .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
            .map(exercise => {
                return {
                    calories: exercise.calories,
                    description: exercise.description,
                    created_at: new Date(exercise.created_at).toLocaleString()
                }
            })

    } else if (datasetType === "browseBodyMeasurement") {
        if (visualType === "tableButton") {
            dataset.headers = type => ["value", "created_at"]
        } else {
            dataset.headers = type => ["value"]
        }
        dataset.data = type => UserBodyMeasurements.filter(bodyMeasurement => bodyMeasurement.type === type)
            .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
            .map(bodyMeasurement => {
                return {
                    value: bodyMeasurement.value,
                    created_at: new Date(bodyMeasurement.created_at).toLocaleString()
                }
            })
    }
    return dataset
}

function updateBrowseTable(headers, data) {
    const tableHeaderDom = document.querySelector("#browseTableHeader")
    const tableBodyDom = document.querySelector("#browseTableBody")
    // Clear existing content
    tableHeaderDom.innerHTML = ""
    tableBodyDom.innerHTML = ""
    if (data.length === 0 || headers.length === 0) {
        return
    }
    // Create table body
    for (let i = 0; i < data.length; i++) {
        const trDom = document.createElement("tr")
        const idDom = document.createElement("td")
        idDom.innerText = String(i + 1)
        trDom.appendChild(idDom)
        for (let k of headers) {
            const tdDom = document.createElement("td")
            tdDom.innerText = data[i][k]
            trDom.appendChild(tdDom)
        }
        tableBodyDom.appendChild(trDom)
    }
    // Create table header
    const tableHeaderRowDom = document.createElement("tr")
    const headersWithID = ["#"].concat(headers)
    for (let i = 0; i < headersWithID.length; i++) {
        const thDom = document.createElement("th")
        thDom.setAttribute("scope", "col")
        thDom.innerText = formatName(headersWithID[i])
        tableHeaderRowDom.appendChild(thDom)
    }
    tableHeaderDom.appendChild(tableHeaderRowDom)
}

/**
 * Update the charts based on the selected type.
 */
function updateBrowseChart(headers, data) {
    const chartContainer = document.querySelector("#chartCard")
    chartContainer.innerHTML = ""
    if (data.length === 0 || headers.length === 0) {
        return
    }
    for (let i = 0; i < headers.length; i++) {
        const chartDiv = document.createElement("div")
        chartDiv.classList.add("chart", "mb-4")
        const canvas = document.createElement("canvas")
        chartDiv.appendChild(canvas)
        chartContainer.appendChild(chartDiv)
        new Chart(canvas, {
            type: "line",
            data: {
                labels: data.map(item => item.created_at),
                datasets: [{
                    label: headers[i],
                    data: data.map(item => item[headers[i]]),
                    borderColor: "rgba(75, 192, 192, 1)",
                    backgroundColor: "rgba(75, 192, 192, 0.2)",
                    borderWidth: 1
                }]
            }
        })
    }
}

function renderDataTypeOptions() {
    let options
    const datasetType = document.querySelector("input[name='dataset']:checked").id
    if (datasetType === "browseExercise") {
        options = ExercisesTypes
    } else if (datasetType === "browseCalorieIntake") {
        options = ["Calories"]
    } else if (datasetType === "browseBodyMeasurement") {
        options = BodyMeasurementTypes
    }

    const select = document.querySelector("#dataTypeSelect")
    select.innerHTML = ""
    for (const key in options) {
        const opt = document.createElement("option")
        opt.value = key
        opt.textContent = options[key]
        select.appendChild(opt)
    }
}

function renderDataView() {
    const dataType = document.querySelector("#dataTypeSelect").value
    const datasetType = document.querySelector("input[name='dataset']:checked").id
    const visualType = document.querySelector("input[name=\"visualType\"]:checked").id
    const dataset = createDataset(datasetType, visualType)

    const headers = dataset.headers(dataType)
    const data = dataset.data(dataType)
    if (visualType === "tableButton") {
        updateBrowseTable(headers, data)
    } else {
        updateBrowseChart(headers, data)
    }
}
