import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    label = next((l for l in state["labels"] if l["name"] == "Receipts"), None)
    if label:
        return False, "Label 'Receipts' still exists."
    for email in state["emails"]:
        if "label_13" in email.get("labels", []):
            return False, f"Email {email['id']} still has deleted label 'label_13'."
    return True, "Label 'Receipts' deleted and removed from all emails."
