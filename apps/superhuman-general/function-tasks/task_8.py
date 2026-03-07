import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if e["subject"] == "Patent Filing Deadline - April 15" and e["from"]["email"] == "james.obrien@legalwise.com"), None)
    if not email:
        return False, "Email 'Patent Filing Deadline - April 15' not found."
    if email.get("remindAt") is not None:
        return False, f"Reminder is still set: {email['remindAt']}"
    return True, "Reminder cleared from 'Patent Filing Deadline - April 15'."
