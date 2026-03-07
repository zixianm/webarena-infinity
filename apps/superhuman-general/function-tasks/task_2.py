import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if e["subject"] == "Re: Infrastructure Migration Plan" and e["from"]["email"] == "tom.bradley@acmecorp.com"), None)
    if not email:
        return False, "Email 'Re: Infrastructure Migration Plan' not found."
    if email["isRead"]:
        return False, "Email is still read."
    return True, "Email 'Re: Infrastructure Migration Plan' is marked as unread."
