import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    settings = state.get("settings", {})
    val = settings.get("timezone")
    if val != "America/Los_Angeles":
        return False, f"Primary timezone: expected 'America/Los_Angeles', got '{val}'"
    return True, "Primary timezone set to 'America/Los_Angeles'."
