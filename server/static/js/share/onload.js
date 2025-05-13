restoreFilterState()

// Search friends functionality
document.getElementById("searchFriend").addEventListener("input", function () {
    searchFriend()
})

// Modal event handlers
document.getElementById("sharesSentModal").addEventListener("show.bs.modal", function () {
    renderSharesDetail("sent", SharesSent)
})
document.getElementById("sharesReceivedModal").addEventListener("show.bs.modal", function () {
    renderSharesDetail("received", SharesReceived)
})

const fieldIdList = ["start_date", "end_date", "subTypeCheckboxes",]
fieldIdList.forEach(id => {
    const field = document.getElementById(id)
    if (field) {
        field.addEventListener("change", function () {
            fetchAndPreviewShareData()
            saveFilterState()
        })
    }
})
document.getElementById("chartType").addEventListener("change", function () {
    sharedDataTypeChanged()
    fetchAndPreviewShareData()
    saveFilterState()
})

// Initialize preview data on page load
updateScopeHidden()
fetchAndPreviewShareData()