import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    settings = state.get("settings", {})
    section = settings.get("notifications", {})
    val = section.get("desktop")
    if val is not False:
        return False, f"Desktop notifications: expected False, got {val}"
    return True, "Desktop notifications: False."
