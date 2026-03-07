import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if e["subject"] == "Partnership Opportunity - FinancePlus x Acme" and e["from"]["email"] == "david.kim@financeplus.com"), None)
    if not email:
        return False, "Email not found."
    finance_label = next((l for l in state["labels"] if l["name"] == "Finance"), None)
    if not finance_label:
        return False, "Label 'Finance' not found."
    if finance_label["id"] not in email.get("labels", []):
        return False, "Label 'Finance' not applied to email."
    return True, "Label 'Finance' applied to email."
