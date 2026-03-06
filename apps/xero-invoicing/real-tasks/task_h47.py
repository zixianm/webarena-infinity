import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Summit Health Group (con_014) has a draft repeating invoice (rep_005)
    # and an overdue invoice INV-0051 (due 2026-03-01)
    inv = next((i for i in state["invoices"] if i["number"] == "INV-0051"), None)
    if not inv:
        return False, "Invoice INV-0051 not found."

    if inv["status"] != "paid":
        return False, f"INV-0051 status is '{inv['status']}', expected 'paid'."

    if abs(inv["amountDue"]) > 0.01:
        return False, f"INV-0051 amountDue is {inv['amountDue']}, expected 0."

    if not inv.get("payments"):
        return False, "INV-0051 has no payments recorded."

    return True, "INV-0051 (Summit Health, client with draft repeating invoice) fully paid."
