import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if e["subject"] == "Partnership Opportunity - FinancePlus x Acme" and e["from"]["email"] == "david.kim@financeplus.com"), None)
    if not email:
        return False, "Email 'Partnership Opportunity - FinancePlus x Acme' not found."
    if not email["isStarred"]:
        return False, "Email is not starred."
    return True, "Email 'Partnership Opportunity - FinancePlus x Acme' is starred."
