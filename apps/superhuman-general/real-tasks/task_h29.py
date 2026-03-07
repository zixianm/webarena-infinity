import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    events = state.get("calendarEvents", [])
    if not events:
        return False, "No calendar events found."

    # Find event with most attendees
    max_event = max(events, key=lambda e: len(e.get("attendees", [])))
    max_count = len(max_event.get("attendees", []))

    if max_count == 0:
        return False, "No event has any attendees."

    # The All-Hands Meeting should have the most attendees (8)
    all_hands = None
    for e in events:
        if e.get("title") == "All-Hands Meeting":
            all_hands = e
            break

    if all_hands is None:
        return False, "All-Hands Meeting event not found."

    location = all_hands.get("location", "")
    if "main auditorium" not in location.lower():
        return False, f"All-Hands Meeting location is '{location}', expected 'Main Auditorium'."

    return True, "All-Hands Meeting (most attendees) location updated to 'Main Auditorium'."
