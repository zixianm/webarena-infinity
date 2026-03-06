import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # INV-0056 and INV-0057 were both awaiting approval
    for num in ["INV-0056", "INV-0057"]:
        inv = next((i for i in state["invoices"] if i["number"] == num), None)
        if not inv:
            return False, f"Invoice {num} not found."
        if inv["status"] != "awaiting_payment":
            return False, f"{num} status is '{inv['status']}', expected 'awaiting_payment' (approved)."
        if not inv.get("sentAt"):
            return False, f"{num} has not been sent."

    return True, "Both INV-0056 and INV-0057 approved and sent."
