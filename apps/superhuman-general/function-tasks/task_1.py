import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if e["subject"] == "Q2 Product Roadmap - Final Review" and e["from"]["email"] == "sarah.chen@acmecorp.com"), None)
    if not email:
        return False, "Email 'Q2 Product Roadmap - Final Review' not found."
    if not email["isRead"]:
        return False, "Email is still unread."
    return True, "Email 'Q2 Product Roadmap - Final Review' is marked as read."
