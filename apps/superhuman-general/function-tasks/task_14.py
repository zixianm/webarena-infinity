import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if e["subject"] == "Q2 Product Roadmap - Final Review" and e["from"]["email"] == "sarah.chen@acmecorp.com"), None)
    if not email:
        return False, "Email 'Q2 Product Roadmap - Final Review' not found."
    work_label = next((l for l in state["labels"] if l["name"] == "Work"), None)
    if not work_label:
        return False, "Label 'Work' not found."
    if work_label["id"] in email.get("labels", []):
        return False, "Label 'Work' still on email."
    return True, "Label 'Work' removed from email."
