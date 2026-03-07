import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    shortcuts = state.get("settings", {}).get("keyboard", {}).get("shortcuts")
    if shortcuts is False:
        return True, "Keyboard shortcuts have been successfully turned off."
    return False, f"Keyboard shortcuts are still enabled (value: {shortcuts})."
