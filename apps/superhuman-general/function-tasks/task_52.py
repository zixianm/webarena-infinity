import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    settings = state.get("settings", {})
    val = settings.get("swipeLeft")
    if val != "trash":
        return False, f"Swipe left action: expected 'trash', got '{val}'"
    return True, "Swipe left action set to 'trash'."
