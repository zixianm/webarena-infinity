import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    notifications = state.get("settings", {}).get("notifications", {})
    desktop = notifications.get("desktop")
    if desktop is False:
        return True, "Desktop notifications are disabled."
    return False, f"Expected desktop notifications to be False, but got {desktop!r}."
