import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    label = next((l for l in state["labels"] if l["name"] == "Partnerships"), None)
    if not label:
        return False, "Label 'Partnerships' not found."
    if label.get("type") != "user":
        return False, f"Label type should be 'user', got '{label.get('type')}'."
    if label.get("color") != "#FF5722":
        return False, f"Label color should be '#FF5722', got '{label.get('color')}'."
    return True, "Label 'Partnerships' created with correct color."
