import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    al = next((a for a in state["autoLabels"] if a["name"] == "Team Update"), None)
    if not al:
        return False, "Auto label 'Team Update' not found."
    if al["enabled"]:
        return False, "Auto label 'Team Update' is still enabled."
    return True, "Auto label 'Team Update' is disabled."
