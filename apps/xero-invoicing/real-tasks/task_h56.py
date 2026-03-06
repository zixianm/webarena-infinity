import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # INV-0045 (Pinnacle Construction) should have payments removed and be voided
    inv = next((i for i in state["invoices"] if i["number"] == "INV-0045"), None)
    if not inv:
        return False, "Invoice INV-0045 not found."

    if inv["status"] != "voided":
        return False, f"INV-0045 status is '{inv['status']}', expected 'voided'."

    if inv.get("payments"):
        return False, f"INV-0045 still has {len(inv['payments'])} payment(s), expected none."

    return True, "INV-0045 payments removed and invoice voided."
