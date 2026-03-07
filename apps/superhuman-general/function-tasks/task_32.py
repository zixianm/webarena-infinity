import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    al = next((a for a in state["autoLabels"] if a["name"] == "Shipping Update"), None)
    if not al:
        return False, "Auto label 'Shipping Update' not found."
    if not al["enabled"]:
        return False, "Auto label 'Shipping Update' is not enabled."
    return True, "Auto label 'Shipping Update' is enabled."
