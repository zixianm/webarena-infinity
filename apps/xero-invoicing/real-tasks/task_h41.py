import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # The invoice with the largest outstanding balance is INV-0055 (TechVault, $41,800)
    inv = next((i for i in state["invoices"] if i["number"] == "INV-0055"), None)
    if not inv:
        return False, "Invoice INV-0055 not found."

    if inv["status"] != "paid":
        return False, f"INV-0055 status is '{inv['status']}', expected 'paid'."

    if abs(inv["amountDue"]) > 0.01:
        return False, f"INV-0055 amountDue is {inv['amountDue']}, expected 0."

    if not inv.get("payments"):
        return False, "INV-0055 has no payments recorded."

    return True, "INV-0055 (largest outstanding balance) fully paid."
