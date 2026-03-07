import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    events = state.get("calendarEvents", [])
    if not events:
        return False, "No calendar events found in state."

    required_attendees = {"emily.r@venturelabs.co", "patrick.oneil@acmecorp.com"}

    for event in events:
        title = event.get("title", "")
        if "board meeting" not in title.lower():
            continue

        date = event.get("date", "")
        if date != "2026-03-10":
            continue

        start_time = event.get("startTime", "")
        if start_time != "10:00":
            continue

        end_time = event.get("endTime", "")
        if end_time != "12:00":
            continue

        location = event.get("location", "")
        if "board room" not in location.lower():
            continue

        attendees = set(event.get("attendees", []))
        if not required_attendees.issubset(attendees):
            missing = required_attendees - attendees
            return False, (
                f"Found matching board meeting event but missing attendees: {missing}. "
                f"Current attendees: {attendees}"
            )

        return True, (
            "Board meeting event found on 2026-03-10 from 10:00-12:00 at Board Room "
            "with Emily Rodriguez and Patrick O'Neil as attendees."
        )

    return False, (
        "No calendar event found matching: title contains 'Board Meeting', "
        "date 2026-03-10, 10:00-12:00, location contains 'Board Room'."
    )
