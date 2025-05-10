function toReadable(str) {
    return str.replace(/([a-z])([A-Z])/g, "$1 $2")
        .replace(/([A-Z]+)([A-Z][a-z])/g, "$1 $2")
        .replace(/_/g, " ")
        .replace(/\b\w/g, char => char.toUpperCase())
}

function updateBrowseTableOptions(options) {
    const select = document.querySelector("#browseTableTypeSelect")
    select.innerHTML = ""
    for (const key in options) {
        const opt = document.createElement("option")
        opt.value = key
        opt.textContent = options[key]
        select.appendChild(opt)
    }
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
            let value=data[i][k]
            if (k === "created_at") {
                value= new Date(value)
                value=value.toLocaleString()
            }
            tdDom.innerText = value
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
        thDom.innerText = toReadable(headersWithID[i])
        tableHeaderRowDom.appendChild(thDom)
    }
    tableHeaderDom.appendChild(tableHeaderRowDom)
}