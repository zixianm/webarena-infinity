import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if e["subject"] == "FY2026 Budget Summary" and e["from"]["email"] == "priya.sharma@acmecorp.com"), None)
    if not email:
        return False, "Email 'FY2026 Budget Summary' not found."
    if email["isStarred"]:
        return False, "Email is still starred."
    return True, "Email 'FY2026 Budget Summary' is unstarred."
