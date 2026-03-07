import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    al = next((a for a in state["autoLabels"] if a["name"] == "Support Ticket"), None)
    if al:
        return False, "Auto label 'Support Ticket' still exists."
    return True, "Auto label 'Support Ticket' deleted."
