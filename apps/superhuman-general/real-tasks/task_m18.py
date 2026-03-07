import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    auto_labels = state.get("autoLabels", [])

    for label in auto_labels:
        name = label.get("name", "")
        if name == "Support Ticket":
            return False, (
                "Auto label 'Support Ticket' still exists. It should have been deleted."
            )

    return True, "Auto label 'Support Ticket' has been successfully deleted."
