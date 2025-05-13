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

function searchFriend() {
    const username = document.getElementById("searchFriend").value.trim()
    const friendSelect = document.getElementById("friendacSelect")
    friendSelect.innerHTML = ""
    if (!username) return
    fetch(`/user/${encodeURIComponent(username)}`)
        .then(res => res.json())
        .then(res => {
            if (res.code === 1 && Array.isArray(res.data)) {
                res.data.forEach(user => {
                    const option = document.createElement("option")
                    option.value = user.id
                    option.text = `${user.nickname}（@${user.username}）`
                    friendSelect.appendChild(option)
                })
            }
        })
}

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
    if (!confirm("Are you sure you want to delete this share record?")) return
    fetch("/share/" + id, {method: "DELETE"})
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok")
            }
            return response.json()
        })
        .then(data => location.reload())
}

function renderSharesDetail(type, data) {
    const detailId = type === "sent" ? "sharesSentDetail" : "sharesReceivedDetail"
    const container = document.getElementById(detailId)
    container.innerHTML = ""

    data.forEach(record => {
        // Create card element
        const card = document.createElement("div")
        card.className = "card mb-2"

        const cardBody = document.createElement("div")
        cardBody.className = "card-body"

        const headerRow = document.createElement("div")
        headerRow.className = "d-flex justify-content-between align-items-center mb-2"

        const title = document.createElement("h6")
        title.className = "card-title mb-0"
        title.textContent = type === "sent" ? record.receiver : record.sender

        // Create button group
        const buttonGroup = document.createElement("div")
        buttonGroup.className = "btn-group btn-group-sm"

        // View button
        const viewButton = document.createElement("button")
        viewButton.className = "btn btn-outline-success"
        viewButton.setAttribute("type", "button")
        viewButton.setAttribute("aria-label", "View")

        const viewIcon = document.createElement("i")
        viewIcon.className = "bi bi-eye"
        viewButton.appendChild(viewIcon)

        viewButton.addEventListener("click", () => {
            location.href = `/share/${record.id}`
        })

        // Delete button
        const deleteButton = document.createElement("button")
        deleteButton.className = "btn btn-outline-danger"
        deleteButton.setAttribute("type", "button")
        deleteButton.setAttribute("aria-label", "Delete")

        const deleteIcon = document.createElement("i")
        deleteIcon.className = "bi bi-trash"
        deleteButton.appendChild(deleteIcon)

        deleteButton.addEventListener("click", () => {
            deleteShareRecord(record.id)
        })

        // Add buttons to group
        buttonGroup.appendChild(viewButton)
        buttonGroup.appendChild(deleteButton)

        headerRow.appendChild(title)
        headerRow.appendChild(buttonGroup)

        const scopeContainer = document.createElement("div")
        scopeContainer.className = "card-text"

        // Render scope data
        renderScope(scopeContainer, record.scope)

        const timeInfo = document.createElement("div")
        timeInfo.className = "text-muted small"
        timeInfo.textContent = new Date(record.created_at).toLocaleString()

        cardBody.appendChild(headerRow)
        cardBody.appendChild(scopeContainer)
        cardBody.appendChild(timeInfo)
        card.appendChild(cardBody)
        container.appendChild(card)
    })
}

function renderScope(container, scope) {
    if (!scope) return

    Object.entries(scope).forEach(([category, items]) => {
        if (items.length === 0) return

        // Create category title
        const categoryTitle = document.createElement("div")
        categoryTitle.className = "fw-bold mt-2"
        categoryTitle.textContent = formatName(category) + ":"
        container.appendChild(categoryTitle)

        // Create items list
        const itemsList = document.createElement("div")
        itemsList.className = "ms-3"

        items.forEach(item => {
            const itemElement = document.createElement("span")
            itemElement.className = "badge bg-light text-dark me-2 mb-1"
            itemElement.textContent = formatName(item)
            itemsList.appendChild(itemElement)
        })

        container.appendChild(itemsList)
    })
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

function getColumns(type) {
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
    header.innerHTML = columns.map(col => `<th>${formatName(col)}</th>`).join("")
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

    const columns = getColumns(type)

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