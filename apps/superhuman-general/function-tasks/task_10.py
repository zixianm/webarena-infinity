import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if "Complete Your Survey" in e["subject"] and "Gift Card" in e["subject"]), None)
    if not email:
        return False, "Email 'Complete Your Survey - Win a $500 Gift Card' not found."
    if email["isTrashed"]:
        return False, "Email is still in Trash."
    return True, "Email restored from Trash."
