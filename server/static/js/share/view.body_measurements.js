function processBodyMeasurements(data) {
    const grouped = {
        WEIGHT: {label: "Weight", unit: "kg", data: []},
        HEIGHT: {label: "Height", unit: "cm", data: []},
        BODY_FAT: {label: "Body Fat", unit: "%", data: []}
    }

    data.forEach(entry => {
        const type = entry.type.replace(/_/g, " ")
        const metric = grouped[entry.type]
        if (metric) {
            metric.data.push({
                date: new Date(entry.created_at),
                value: entry.value,
                formattedDate: new Date(entry.created_at).toLocaleDateString()
            })
        }
    })

    Object.values(grouped).forEach(metric => {
        metric.data.sort((a, b) => a.date - b.date)
    })

    return grouped
}

function createWeightChart(processedData) {
    const weightData = processedData.WEIGHT

    new Chart(document.getElementById("weightChart"), {
        type: "line", data: {
            labels: weightData.data.map(d => d.formattedDate), datasets: [{
                label: `${weightData.label} (${weightData.unit})`,
                data: weightData.data.map(d => d.value),
                borderColor: "rgb(255, 99, 132)",
                tension: 0.3,
                fill: false
            }]
        }, options: {
            responsive: true, scales: {
                x: {
                    title: {display: true, text: "Date"}
                }, y: {
                    title: {display: true, text: weightData.unit}
                }
            }
        }
    })
}

function createBodyFatChart(processedData) {
    const fatData = processedData.BODY_FAT
    const ctx = document.getElementById("bodyFatChart")

    const config = {
        data: {
            labels: fatData.data.map(d => d.formattedDate), datasets: [{
                label: `${fatData.label} (${fatData.unit})`, data: fatData.data.map(d => d.value),
            }]
        }, options: {
            responsive: true, scales: {y: {beginAtZero: true}}
        }
    }

    config.type = fatData.data.length > 3 ? "line" : "bar"
    config.data.datasets[0].backgroundColor = "rgba(54, 162, 235, 0.5)"

    new Chart(ctx, config)
}

function createMetricDashboard(processedData) {
    const latest = {
        weight: processedData.WEIGHT.data.slice(-1)[0]?.value || "-",
        height: processedData.HEIGHT.data[0]?.value || "-",
        bodyFat: processedData.BODY_FAT.data.slice(-1)[0]?.value || "-"
    }

    // 更新DOM元素
    document.getElementById("latestWeight").innerHTML = `
    <h3>Weight</h3>
    <div class="value">${latest.weight}</div>
    <div class="unit">${processedData.WEIGHT.unit}</div>
  `

    document.getElementById("heightDisplay").innerHTML = `
    <h3>Height</h3>
    <div class="value">${latest.height}</div>
    <div class="unit">${processedData.HEIGHT.unit}</div>
  `

    document.getElementById("bodyFatPercentage").innerHTML = `
    <h3>Body Fat</h3>
    <div class="value">${latest.bodyFat}</div>
    <div class="unit">${processedData.BODY_FAT.unit}</div>
  `
}

function visualizeBodyMeasurements(rawData) {
    const processed = processBodyMeasurements(rawData.body_measurements)

    createWeightChart(processed)
    if (processed.BODY_FAT.data.length > 0) {
        createBodyFatChart(processed)
    }

    createMetricDashboard(processed)
}

visualizeBodyMeasurements(SharedData)