function getNextDateForDay(dayName) {
    const dayMap = {
        "sunday": 0, "monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4, "friday": 5, "saturday": 6
    }

    const targetDay = dayName.toLowerCase()
    const targetIdx = dayMap[targetDay]

    if (targetIdx === undefined) {
        throw new Error(`Invalid day name: ${dayName}`)
    }

    const today = new Date()
    const todayIdx = today.getDay() // 0-6 (Sunday=0)

    let delta = targetIdx - todayIdx
    if (delta <= 0) {
        delta += 7
    }

    const nextDate = new Date(today)
    nextDate.setDate(today.getDate() + delta)
    return nextDate
}

function renderCalendar(calendar_events) {
    const calendarEl = document.getElementById("calendar")
    if (calendarEl) {
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: "dayGridMonth",
            height: 330,
            headerToolbar: {
                start: "title", center: "", end: "prev,next"
            },
            buttonText: {
                today: "Today"
            },
            events: calendar_events,
            eventDisplay: "auto",
            dayHeaders: true,
            dayHeaderFormat: {weekday: "narrow"},
            eventDidMount: function (info) {
                // Find the day cell
                const dayCell = info.el.closest(".fc-daygrid-day")
                if (dayCell) {
                    dayCell.classList.add("fc-blue-circle")
                    // Collect all events for this day
                    const dateStr = info.event.startStr
                    const eventsForDay = info.view.calendar.getEvents().filter(function (ev) {
                        return ev.startStr === dateStr
                    })
                    // Combine tooltips
                    var tooltip = eventsForDay.map(function (ev) {
                        return ev.extendedProps.tooltip
                    }).join("\n")
                    // Set tooltip on the day cell (not just the event)
                    dayCell.setAttribute("title", tooltip)
                }
            },
            eventContent: function (arg) {
                return false
            }
        })

        calendar.render()

        function updateTodayButton() {
            const todayBtn = calendarEl.querySelector(".fc-today-button")
            if (todayBtn) {
                const today = new Date()
                const weekday = today.toLocaleDateString("en-US", {weekday: "short"})
                todayBtn.textContent = `Today (${weekday})`
            }
        }

        updateTodayButton()
        calendar.on("datesSet", updateTodayButton)

    }
}

const calendar_events = []
CurrentUser.scheduledExercises.forEach(event => {
    calendar_events.push({
        title: "", start: getNextDateForDay(event.day_of_week), color: "#b3d8fd", extendedProps: {
            "tooltip": event.exercise_type
        }
    })
})
renderCalendar(calendar_events)
