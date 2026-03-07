import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if e["subject"] == "Re: Q1 Sales Numbers" and e["from"]["email"] == "sarah.chen@acmecorp.com"), None)
    if not email:
        return False, "Email 'Re: Q1 Sales Numbers' not found."
    if email["isDone"]:
        return False, "Email is still in Done."
    return True, "Email 'Re: Q1 Sales Numbers' moved back to Inbox."
