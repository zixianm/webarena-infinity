import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Overdue invoices (dueDate < 2026-03-02) that had no prior payments in seed state:
    # INV-0046 (Baxter, due 2026-02-01)
    # INV-0047 (CloudNine, due 2026-02-15)
    # INV-0049 (Coastal Living, due 2026-02-24)
    # INV-0051 (Summit Health, due 2026-03-01)
    # Note: INV-0045 (Pinnacle, due 2026-02-19) had a partial payment, so excluded
    overdue_no_payment = ["INV-0046", "INV-0047", "INV-0049", "INV-0051"]

    for num in overdue_no_payment:
        inv = next((i for i in state["invoices"] if i["number"] == num), None)
        if not inv:
            return False, f"Invoice {num} not found."
        if inv["status"] != "paid":
            return False, f"{num} status is '{inv['status']}', expected 'paid'."
        if abs(inv["amountDue"]) > 0.01:
            return False, f"{num} amountDue is {inv['amountDue']}, expected 0."

    return True, "All overdue invoices without prior payments have been paid."
