import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    settings = state.get("settings", {})
    val = settings.get("secondaryTimezone")
    if val not in ("", None, "none"):
        return False, f"Secondary timezone: expected empty/None, got '{val}'"
    return True, "Secondary timezone set to None."
