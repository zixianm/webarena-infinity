import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    contact = next((c for c in state["contacts"] if c["name"] == "CloudNine Analytics"), None)
    if not contact:
        return False, "Contact CloudNine Analytics not found."

    # CloudNine has two open invoices: INV-0047 ($18,652.70) and INV-0062 ($2,139.50)
    # The smaller one is INV-0062
    inv = next((i for i in state["invoices"] if i["number"] == "INV-0062"), None)
    if not inv:
        return False, "Invoice INV-0062 not found."

    if inv["status"] != "paid":
        return False, f"INV-0062 status is '{inv['status']}', expected 'paid'."

    if abs(inv["amountDue"]) > 0.01:
        return False, f"INV-0062 amountDue is {inv['amountDue']}, expected 0."

    if not inv.get("payments"):
        return False, "INV-0062 has no payments recorded."

    # Verify the larger one is still unpaid
    larger = next((i for i in state["invoices"] if i["number"] == "INV-0047"), None)
    if larger and larger["status"] == "paid":
        return False, "INV-0047 (the larger invoice) was also paid - only the smaller should be paid."

    return True, "INV-0062 (CloudNine's smaller invoice) fully paid."
