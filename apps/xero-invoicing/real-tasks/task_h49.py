import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # INV-0045 is Pinnacle Construction's invoice with PO-9012 reference
    inv = next((i for i in state["invoices"] if i["number"] == "INV-0045"), None)
    if not inv:
        return False, "Invoice INV-0045 not found."

    # Original had $4,950 paid. We expect an additional $2,000 payment.
    total_paid = sum(p["amount"] for p in inv.get("payments", []))
    expected_min = 4950.00 + 2000.00 - 0.01

    if total_paid < expected_min:
        return False, f"Total payments on INV-0045 are ${total_paid:.2f}, expected at least $6,950."

    # Check that a $2,000 payment exists
    has_2k = any(abs(p["amount"] - 2000.00) < 0.01 for p in inv.get("payments", []))
    if not has_2k:
        return False, "No $2,000 payment found on INV-0045."

    return True, "INV-0045 has $2,000 partial payment recorded."
