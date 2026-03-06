import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # CN-0012 is CloudNine's open credit note ($2,035)
    cn = next((c for c in state["creditNotes"] if c["number"] == "CN-0012"), None)
    if not cn:
        return False, "Credit note CN-0012 not found."

    if not cn.get("allocations"):
        return False, "CN-0012 has no allocations."

    # INV-0047 (due 2026-02-15) is CloudNine's soonest-due invoice
    inv = next((i for i in state["invoices"] if i["number"] == "INV-0047"), None)
    if not inv:
        return False, "Invoice INV-0047 not found."

    alloc = next((a for a in cn["allocations"] if a["invoiceId"] == inv["id"]), None)
    if not alloc:
        return False, "CN-0012 not allocated against INV-0047 (CloudNine's soonest-due invoice)."

    return True, "CN-0012 allocated against INV-0047 (soonest-due CloudNine invoice)."
