import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    auto_labels = state.get("autoLabels", [])
    for label in auto_labels:
        if label.get("name") == "Shipping Update":
            if label.get("enabled") is True:
                return True, "The 'Shipping Update' auto label is now enabled."
            else:
                return False, "The 'Shipping Update' auto label was found but is not enabled."
    return False, "No auto label with name 'Shipping Update' was found."
