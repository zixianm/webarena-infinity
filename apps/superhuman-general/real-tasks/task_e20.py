import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    auto_labels = state.get("autoLabels", [])
    for label in auto_labels:
        if label.get("name") == "Team Update":
            if label.get("enabled") is False:
                return True, "The 'Team Update' auto label has been successfully disabled."
            else:
                return False, "The 'Team Update' auto label was found but is still enabled."
    return False, "No auto label with name 'Team Update' was found."
