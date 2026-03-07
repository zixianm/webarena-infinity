import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    event = next((e for e in state["calendarEvents"] if e["title"] == "Team Lunch"), None)
    if not event:
        return False, "Calendar event 'Team Lunch' not found."
    if event["date"] != "2026-03-10":
        return False, f"Event date should be 2026-03-10, got {event['date']}."
    if event["startTime"] != "12:00":
        return False, f"Start time should be 12:00, got {event['startTime']}."
    if event["endTime"] != "13:00":
        return False, f"End time should be 13:00, got {event['endTime']}."
    if "Cafe Gratitude" not in event.get("location", ""):
        return False, f"Location should contain 'Cafe Gratitude', got '{event.get('location', '')}'."
    return True, "Calendar event 'Team Lunch' created with correct details."
