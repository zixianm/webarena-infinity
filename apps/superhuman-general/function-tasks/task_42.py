import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    settings = state.get("settings", {})
    section = settings.get("readReceipts", {})
    val = section.get("teamSharing")
    if val is not False:
        return False, f"Team read statuses: expected False, got {val}"
    return True, "Team read statuses: False."
