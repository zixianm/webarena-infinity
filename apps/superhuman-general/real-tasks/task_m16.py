import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    meeting_link = settings.get("meetingLink", {})
    auto_add = meeting_link.get("autoAdd")

    if auto_add is False:
        return True, "Auto-adding meeting links to new events is correctly disabled."

    return False, f"Expected meetingLink.autoAdd to be False, but found '{auto_add}'."
