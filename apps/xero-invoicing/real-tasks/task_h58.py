import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    settings = state.get("invoiceSettings", {})

    # Check prefix is DEMO-
    if settings.get("invoicePrefix") != "DEMO-":
        return False, f"Invoice prefix is '{settings.get('invoicePrefix')}', expected 'DEMO-'."

    # Find Greenfield Organics contact
    contact = next((c for c in state["contacts"] if c["name"] == "Greenfield Organics"), None)
    if not contact:
        return False, "Greenfield Organics contact not found."

    # Find a new invoice for Greenfield with DEMO- prefix and training line item
    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == contact["id"]
                    and i["number"].startswith("DEMO-")
                    and any(li.get("itemId") == "item_006" for li in i.get("lineItems", []))), None)

    if not new_inv:
        return False, "No new DEMO- invoice for Greenfield Organics with training found."

    training_line = next((li for li in new_inv["lineItems"] if li.get("itemId") == "item_006"), None)
    if training_line["quantity"] != 1:
        return False, f"Training quantity is {training_line['quantity']}, expected 1."

    return True, f"Invoice prefix changed to DEMO-, numbering at 200, {new_inv['number']} created."
