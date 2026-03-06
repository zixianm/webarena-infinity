import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Check that 'Consulting' theme exists
    theme = next((t for t in state["brandingThemes"] if t["name"] == "Consulting"), None)
    if not theme:
        return False, "Branding theme 'Consulting' not found."

    # Find Wellington & Partners contact
    contact = next((c for c in state["contacts"] if "Wellington" in c["name"]), None)
    if not contact:
        return False, "Wellington & Partners contact not found."

    # Find new invoice for Wellington in NZD using the Consulting theme
    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == contact["id"]
                    and i["currency"] == "NZD"
                    and i["brandingThemeId"] == theme["id"]
                    and i["number"] not in ["INV-0066"]), None)

    if not new_inv:
        return False, "No new NZD invoice for Wellington & Partners using 'Consulting' theme found."

    # Check consulting line item (4 hours)
    consult_line = next((li for li in new_inv.get("lineItems", [])
                         if li.get("itemId") == "item_002"), None)
    if not consult_line:
        return False, "Invoice doesn't have a consulting line item."

    if consult_line["quantity"] != 4:
        return False, f"Consulting quantity is {consult_line['quantity']}, expected 4."

    return True, f"Consulting theme created and {new_inv['number']} invoiced in NZD."
