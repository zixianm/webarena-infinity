import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    settings = state.get("settings", {})
    section = settings.get("autoReminders", {})
    val = section.get("defaultTime")
    if val != "14:00":
        return False, f"Auto reminder default time: expected '14:00', got '{val}'"
    return True, "Auto reminder default time set to '14:00'."
