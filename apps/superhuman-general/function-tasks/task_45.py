import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    settings = state.get("settings", {})
    section = settings.get("meetingLink", {})
    val = section.get("autoAdd")
    if val is not False:
        return False, f"Auto-add meeting links: expected False, got {val}"
    return True, "Auto-add meeting links: False."
