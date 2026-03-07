import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    settings = state.get("settings", {})
    section = settings.get("askAi", {})
    val = section.get("enabled")
    if val is not False:
        return False, f"Ask AI: expected False, got {val}"
    return True, "Ask AI: False."
