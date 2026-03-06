import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Find Vanguard Security Systems contact
    contact = next((c for c in state["contacts"] if c["name"] == "Vanguard Security Systems"), None)
    if not contact:
        return False, "Vanguard Security Systems contact not found."

    # Find new repeating invoice for Vanguard (not rep_004 which is their existing one)
    new_ri = next((ri for ri in state["repeatingInvoices"]
                   if ri["contactId"] == contact["id"]
                   and ri["id"] != "rep_004"), None)

    if not new_ri:
        return False, "No new repeating invoice found for Vanguard Security Systems."

    if new_ri.get("frequency") != "weekly":
        return False, f"Frequency is '{new_ri.get('frequency')}', expected 'weekly'."

    if new_ri.get("brandingThemeId") != "theme_retail":
        return False, f"Theme is '{new_ri.get('brandingThemeId')}', expected 'theme_retail'."

    if new_ri.get("saveAs") != "approved_for_sending":
        return False, f"saveAs is '{new_ri.get('saveAs')}', expected 'approved_for_sending'."

    if new_ri.get("endDate") != "2026-12-31":
        return False, f"End date is '{new_ri.get('endDate')}', expected '2026-12-31'."

    # Check for dev hours line item
    dev_line = next((li for li in new_ri.get("lineItems", [])
                     if li.get("itemId") == "item_001"), None)
    if not dev_line:
        return False, "No development line item found."

    if dev_line["quantity"] != 2:
        return False, f"Dev quantity is {dev_line['quantity']}, expected 2."

    return True, f"Weekly repeating invoice for Vanguard created with Retail template."
