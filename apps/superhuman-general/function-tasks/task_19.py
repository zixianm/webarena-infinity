import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if e["subject"] == "EuroDesign Conference - Speaker Invitation" and e["from"]["email"] == "sophie.l@eurodesign.fr"), None)
    if not email:
        return False, "Email 'EuroDesign Conference - Speaker Invitation' not found."
    if not email["isDone"]:
        return False, "Email is not marked as Done."
    return True, "Email 'EuroDesign Conference - Speaker Invitation' marked as Done."
