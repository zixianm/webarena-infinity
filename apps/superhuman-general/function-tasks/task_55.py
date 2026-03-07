import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    settings = state.get("settings", {})
    section = settings.get("notifications", {})
    val = section.get("alertMinutes")
    if val != 30:
        return False, f"Calendar alert minutes: expected '30', got '{val}'"
    return True, "Calendar alert minutes set to '30'."
