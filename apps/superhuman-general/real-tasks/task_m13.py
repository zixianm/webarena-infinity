import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    auto_drafts = settings.get("autoDrafts", {})
    draft_type = auto_drafts.get("type")

    if draft_type == "scheduling":
        return True, "Auto drafts type is correctly set to scheduling mode."

    return False, f"Expected auto drafts type 'scheduling', but found '{draft_type}'."
