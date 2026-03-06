import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    contact = next((c for c in state["contacts"] if c["name"] == "Coastal Living Interiors"), None)
    if not contact:
        return False, "Coastal Living Interiors contact not found."

    # Find new credit note for Coastal Living with Widget A
    new_cn = next((cn for cn in state["creditNotes"]
                   if cn["contactId"] == contact["id"]
                   and cn["number"] not in ["CN-0008", "CN-0009", "CN-0010", "CN-0011", "CN-0012"]
                   and any(li.get("itemId") == "item_011" for li in cn.get("lineItems", []))), None)

    if not new_cn:
        return False, "No new credit note with Widget A found for Coastal Living Interiors."

    widget_line = next((li for li in new_cn["lineItems"] if li.get("itemId") == "item_011"), None)
    if widget_line["quantity"] != 2:
        return False, f"Widget A quantity is {widget_line['quantity']}, expected 2."

    # Must be approved (status awaiting_payment or paid)
    if new_cn["status"] not in ["awaiting_payment", "paid"]:
        return False, f"Credit note status is '{new_cn['status']}', expected approved."

    # Must be allocated against INV-0049
    inv = next((i for i in state["invoices"] if i["number"] == "INV-0049"), None)
    if not inv:
        return False, "Invoice INV-0049 not found."

    alloc = next((a for a in new_cn.get("allocations", []) if a["invoiceId"] == inv["id"]), None)
    if not alloc:
        return False, "Credit note not allocated against INV-0049."

    return True, f"Credit note {new_cn['number']} for 2 Widget A created, approved, and allocated to INV-0049."
