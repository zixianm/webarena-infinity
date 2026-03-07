import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if e["subject"] == "Logistics Update - Office Equipment Delivery" and e["from"]["email"] == "carlos.m@logisticspro.net"), None)
    if not email:
        return False, "Email 'Logistics Update - Office Equipment Delivery' not found."
    if not email["isTrashed"]:
        return False, "Email is not in Trash."
    return True, "Email 'Logistics Update - Office Equipment Delivery' moved to Trash."
