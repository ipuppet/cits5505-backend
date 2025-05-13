restoreFilterState()

// Search friends functionality
document.getElementById("searchFriend").addEventListener("input", function () {
    const username = this.value.trim()
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
                    option.text = user.nickname ? `${user.nickname}（${user.username}）` : user.username
                    friendSelect.appendChild(option)
                })
            }
        })
})

// Modal event handlers
const sentModal = document.getElementById("sentSharesModal")
sentModal && sentModal.addEventListener("show.bs.modal", function () {
    renderSharesDetail("sent", [])
})
const receivedModal = document.getElementById("receivedSharesModal")
receivedModal && receivedModal.addEventListener("show.bs.modal", function () {
    renderSharesDetail("received", [])
})

const fieldIdList = ["start_date", "end_date", "chartType", "subTypeCheckboxes",]
fieldIdList.forEach(id => {
    const field = document.getElementById(id)
    if (field) {
        field.addEventListener("change", function () {
            fetchAndPreviewShareData()
            saveFilterState()
        })
    }
})

// Data type selection handler - generates appropriate sub-type filters
document.getElementById("chartType").addEventListener("change", function () {
    sharedDataTypeChanged()
    fetchAndPreviewShareData()
    saveFilterState()
})

// Initialize preview data on page load
updateScopeHidden()
fetchAndPreviewShareData()