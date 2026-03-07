import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    calendar_events = state.get("calendarEvents", [])
    for event in calendar_events:
        if event.get("title") == "Yoga Class" and event.get("date") == "2026-03-07":
            return False, "The 'Yoga Class' event on 2026-03-07 still exists in the calendar."
    return True, "The 'Yoga Class' event on today's calendar has been successfully cancelled."
