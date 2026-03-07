import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if e["subject"] == "Global Health Initiative - Sponsorship Request" and e["from"]["email"] == "ana.g@globalhealth.org"), None)
    if not email:
        return False, "Email 'Global Health Initiative - Sponsorship Request' not found."
    if not email["isDone"]:
        return False, "Email is not marked as Done."
    return True, "Email 'Global Health Initiative - Sponsorship Request' is marked as Done."
