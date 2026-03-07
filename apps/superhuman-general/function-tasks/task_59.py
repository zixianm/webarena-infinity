import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    settings = state.get("settings", {})
    section = settings.get("autoReminders", {})
    val = section.get("mode")
    if val != "external":
        return False, f"Auto reminder mode: expected 'external', got '{val}'"
    return True, "Auto reminder mode set to 'external'."
