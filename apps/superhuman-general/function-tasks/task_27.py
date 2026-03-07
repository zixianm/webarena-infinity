import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    event = next((e for e in state["calendarEvents"] if e["title"] == "Yoga Class" and e["date"] == "2026-03-07"), None)
    if event:
        return False, "Calendar event 'Yoga Class' still exists."
    return True, "Calendar event 'Yoga Class' deleted."
