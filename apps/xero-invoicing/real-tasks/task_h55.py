import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # CloudNine Analytics has the most unpaid invoices (INV-0047 and INV-0062)
    contact = next((c for c in state["contacts"] if c["name"] == "CloudNine Analytics"), None)
    if not contact:
        return False, "CloudNine Analytics contact not found."

    # Find a new invoice for CloudNine with an annual software license
    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == contact["id"]
                    and i["number"] not in ["INV-0047", "INV-0062"]
                    and any(li.get("itemId") == "item_008" for li in i.get("lineItems", []))), None)

    if not new_inv:
        return False, "No new invoice with annual software license found for CloudNine Analytics."

    license_line = next((li for li in new_inv["lineItems"] if li.get("itemId") == "item_008"), None)
    if license_line["quantity"] != 1:
        return False, f"License quantity is {license_line['quantity']}, expected 1."

    if abs(license_line["unitPrice"] - 1200.00) > 0.01:
        return False, f"License unit price is {license_line['unitPrice']}, expected 1200.00."

    return True, f"CloudNine Analytics invoiced for annual software license ({new_inv['number']})."
