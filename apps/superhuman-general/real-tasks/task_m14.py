import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    calendar_events = state.get("calendarEvents", [])

    for event in calendar_events:
        title = (event.get("title") or "").lower()
        date = event.get("date", "")
        start_time = event.get("startTime", "")
        location = (event.get("location") or "").lower()

        if (
            "lunch" in title
            and date == "2026-03-10"
            and start_time == "12:00"
            and "cafe gratitude" in location
        ):
            return True, "Found calendar event for team lunch on 2026-03-10 at 12:00 at Cafe Gratitude."

    return False, (
        "Could not find a calendar event with title containing 'lunch', "
        "date '2026-03-10', startTime '12:00', and location containing 'Cafe Gratitude'. "
        f"Found {len(calendar_events)} calendar event(s)."
    )
