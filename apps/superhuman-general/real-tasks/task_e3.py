import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    notifications = state.get("settings", {}).get("notifications", {})
    sound = notifications.get("sound")
    if sound is False:
        return True, "Sound notifications are disabled."
    return False, f"Expected sound notifications to be False, but got {sound!r}."
