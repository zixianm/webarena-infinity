import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    settings = state.get("settings", {})
    val = settings.get("swipeRight")
    if val != "star":
        return False, f"Swipe right action: expected 'star', got '{val}'"
    return True, "Swipe right action set to 'star'."
