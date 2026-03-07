import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    settings = state.get("settings", {})
    section = settings.get("autoDrafts", {})
    val = section.get("ccTeammate")
    if val is not True:
        return False, f"Auto drafts Cc teammate: expected True, got {val}"
    return True, "Auto drafts Cc teammate: True."
