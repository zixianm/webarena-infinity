import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    auto_drafts = settings.get("autoDrafts", {})
    cc_teammate = auto_drafts.get("ccTeammate")

    if cc_teammate is True:
        return True, "Cc teammate option for auto drafts is correctly enabled."

    return False, f"Expected autoDrafts.ccTeammate to be True, but found '{cc_teammate}'."
