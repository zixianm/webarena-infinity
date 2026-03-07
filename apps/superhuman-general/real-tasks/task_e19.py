import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    swipe_left = state.get("settings", {}).get("swipeLeft")
    if swipe_left == "trash":
        return True, "The swipe left action has been successfully set to Trash."
    return False, f"The swipe left action is '{swipe_left}', expected 'trash'."
