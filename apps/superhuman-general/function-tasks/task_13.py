import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if e["subject"] == "Budget Approval Needed - Marketing Campaign" and e["from"]["email"] == "priya.sharma@acmecorp.com"), None)
    if not email:
        return False, "Email 'Budget Approval Needed - Marketing Campaign' not found."
    urgent_label = next((l for l in state["labels"] if l["name"] == "Urgent"), None)
    if not urgent_label:
        return False, "Label 'Urgent' not found."
    if urgent_label["id"] not in email.get("labels", []):
        return False, f"Label 'Urgent' ({urgent_label['id']}) not applied to email. Email labels: {email.get('labels', [])}"
    return True, "Label 'Urgent' applied to email."
