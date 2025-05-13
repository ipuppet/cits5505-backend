async function fetchSharedRecords(scope) {
    const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone
    const timezoneInput = document.getElementById("timezone")
    timezoneInput.value = browserTimezone
    const response = await fetch(`/share/preview`, {
        method: "POST", headers: {
            "Content-Type": "application/json"
        }, body: JSON.stringify({
            scope,
            timezone: timezoneInput.value,
            start_date: document.getElementById("start_date").value,
            end_date: document.getElementById("end_date").value,
        })
    })
    const data = await response.json()
    if (data.code === 1) {
        return data.data
    } else {
        console.error("Failed to fetch shared records:", data.message)
        return null
    }
}

// Function definitions in global scope
function deleteShareRecord(id) {
    fetch("/share/" + id, {method: "DELETE"})
        .then(response => response.json())
        .then(data => {
            alert("Share record deleted successfully.")
            // Reload share records
            location.reload()
        })
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

// Save filter conditions to sessionStorage
function saveFilterState() {
    const state = {
        start_date: document.getElementById("start_date").value,
        end_date: document.getElementById("end_date").value,
        chartType: document.getElementById("chartType").value,
        exerciseTypes: Array.from(document.querySelectorAll("input[name=\"exerciseType\"]:checked")).map(i => i.value),
        measurementTypes: Array.from(document.querySelectorAll("input[name=\"measurementType\"]:checked")).map(i => i.value),
        achievementTypes: Array.from(document.querySelectorAll("input[name=\"achievementType\"]:checked")).map(i => i.value)
    }
    sessionStorage.setItem("shareFilterState", JSON.stringify(state))
    console.log("Filter state saved (valid for current session):", state)
}

// Restore filter conditions from sessionStorage
function restoreFilterState() {
    const stateStr = sessionStorage.getItem("shareFilterState")
    if (!stateStr) return

    try {
        const state = JSON.parse(stateStr)
        console.log("Restoring filter state:", state)

        // Restore dates
        if (state.start_date) document.getElementById("start_date").value = state.start_date
        if (state.end_date) document.getElementById("end_date").value = state.end_date

        // Restore data type selection
        if (state.chartType) {
            const chartTypeSelect = document.getElementById("chartType")
            chartTypeSelect.value = state.chartType

            sharedDataTypeChanged() // Generate sub-type checkboxes based on the current chart type

            // Trigger change event to generate appropriate sub-type checkboxes
            const event = new Event("change")
            chartTypeSelect.dispatchEvent(event)

            // Wait for sub-type checkboxes to be generated before restoring selection states
            setTimeout(() => {
                // Restore exercise type selection
                if (state.exerciseTypes && state.chartType === "exercises") {
                    state.exerciseTypes.forEach(type => {
                        const checkbox = document.querySelector(`input[name="exerciseType"][value="${type}"]`)
                        if (checkbox) checkbox.checked = true
                    })
                }

                // Restore body measurement type selection
                if (state.measurementTypes && state.chartType === "body_measurements") {
                    state.measurementTypes.forEach(type => {
                        const checkbox = document.querySelector(`input[name="measurementType"][value="${type}"]`)
                        if (checkbox) checkbox.checked = true
                    })
                }

                // Restore achievement type selection
                if (state.achievementTypes && state.chartType === "achievements") {
                    state.achievementTypes.forEach(type => {
                        const checkbox = document.querySelector(`input[name="achievementType"][value="${type}"]`)
                        if (checkbox) checkbox.checked = true
                    })
                }

                // Trigger data preview update
                fetchAndPreviewShareData()
            }, 100)
        }
    } catch (e) {
        console.error("Failed to restore filter state:", e)
    }
}

// TODO: Expand all Sent Shares/Received Shares
function renderSharesDetail(type, data) {
    let html = ""
    data.forEach(record => {
        html += `<div class="card mb-2"><div class="card-body">
            <h6 class="card-title">${type === "sent" ? record.receiver.nickname : record.sender.nickname}</h6>
            <p class="card-text">${record.message}</p>
            <div class="text-muted small">${record.time || ""}</div>
        </div></div>`
    })
    document.getElementById(type === "sent" ? "sentSharesDetail" : "receivedSharesDetail").innerHTML = html
}

function sharedDataTypeChanged() {
    const value = document.getElementById("chartType").value
    const container = document.getElementById("subTypeCheckboxes")
    container.innerHTML = ""

    let options = []
    let name = ""

    if (value === "exercises") {
        options = ExercisesTypes
        name = "exerciseType"
    } else if (value === "body_measurements") {
        options = BodyMeasurementTypes
        name = "measurementType"
    } else if (value === "achievements") {
        options = ExercisesTypes
        name = "achievementType"
    }

    Object.keys(options).forEach(key => {
        const id = `${value}_${key.toLowerCase()}`

        // Create container div
        const formCheck = document.createElement("div")
        formCheck.className = "form-check"

        // Create input element
        const input = document.createElement("input")
        input.className = "form-check-input"
        input.type = "checkbox"
        input.value = key
        input.id = id
        input.name = name

        // Create label element
        const label = document.createElement("label")
        label.className = "form-check-label"
        label.htmlFor = id
        label.textContent = options[key]

        // Assemble the elements
        formCheck.appendChild(input)
        formCheck.appendChild(label)
        container.appendChild(formCheck)
    })
}

function get_columns(type) {
    let columns = ["created_at", "type"]
    if (type === "exercises") {
        // Get selected subtypes for specific header rendering
        const subTypes = Array.from(document.querySelectorAll("#subTypeCheckboxes input:checked")).map(i => i.value)
        for (subType of subTypes) {
            const types = ExercisesMetrics[subType]
            for (type of types) {
                if (!columns.includes(type)) {
                    columns.push(type)
                }
            }
        }
    } else if (type === "body_measurements") {
        columns = columns.concat(["value"])
    } else if (type === "achievements") {
        columns = columns.concat(["milestone"])
    }
    return columns
}

// Dynamic render table headers based on data type
function renderSharePreviewHeader(columns) {
    const header = document.getElementById("sharePreviewHeader")
    header.innerHTML = columns.map(col => `<th>${toReadable(col)}</th>`).join("")
}

// Render preview table with filtered data
function renderSharePreviewTable(columns, data) {
    const tbody = document.querySelector("#sharePreviewTable tbody")
    tbody.innerHTML = ""
    // Handle empty data case
    const empty = document.getElementById("sharePreviewEmpty")
    if (!data || data.length === 0) {
        empty.style.display = ""
        return
    }
    empty.style.display = "none"

    data.forEach(item => {
        const row = document.createElement("tr")
        if (item.metrics) {
            Object.assign(item, item.metrics)
        }
        columns.forEach(column => {
            const cell = document.createElement("td")
            cell.textContent = item[column] || "-"
            row.appendChild(cell)
        })

        tbody.appendChild(row)
    })
}

// Collect and update filter scope values
function updateScopeHidden() {
    const exerciseTypes = Array.from(document.querySelectorAll("input[name=\"exerciseType\"]:checked")).map(i => i.value)
    const bodyMeasurementTypes = Array.from(document.querySelectorAll("input[name=\"measurementType\"]:checked")).map(i => i.value)
    const achievements = Array.from(document.querySelectorAll("input[name=\"achievementType\"]:checked")).map(i => i.value)

    const scope = {
        exercise_types: exerciseTypes, body_measurement_types: bodyMeasurementTypes, achievements: achievements,
    }
    document.getElementById("scopeHidden").value = JSON.stringify(scope)

    // Save current filter conditions to sessionStorage
    saveFilterState()
}

// Fetch data locally and apply filters
async function fetchAndPreviewShareData() {
    updateScopeHidden()
    const scope = JSON.parse(document.getElementById("scopeHidden").value)
    const type = document.getElementById("chartType").value

    const columns = get_columns(type)

    // Render appropriate headers based on data type
    renderSharePreviewHeader(columns)

    // Handle empty type selection
    if (!type) {
        renderSharePreviewTable([], [])
        return
    }

    let list = await fetchSharedRecords(scope)
    renderSharePreviewTable(columns, convertTimezone(list[type]))
}