import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # QU-0024 is the Atlas Engineering collaboration platform quote
    quo = next((q for q in state["quotes"] if q["number"] == "QU-0024"), None)
    if not quo:
        return False, "Quote QU-0024 not found."

    if quo["status"] != "accepted":
        return False, f"QU-0024 status is '{quo['status']}', expected 'accepted'."

    if not quo.get("isInvoiced"):
        return False, "QU-0024 has not been converted to an invoice."

    # Find the new invoice created from this quote
    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == quo["contactId"]
                    and abs(i["total"] - quo["total"]) < 0.01
                    and i["number"] not in ["INV-0042", "INV-0043", "INV-0044", "INV-0045",
                                             "INV-0046", "INV-0047", "INV-0048", "INV-0049",
                                             "INV-0050", "INV-0051", "INV-0052", "INV-0053",
                                             "INV-0054", "INV-0055", "INV-0056", "INV-0057",
                                             "INV-0058", "INV-0059", "INV-0060", "INV-0061",
                                             "INV-0062", "INV-0063", "INV-0064", "INV-0065",
                                             "INV-0066"]), None)

    if not new_inv:
        return False, "No new invoice found matching the quote total for Atlas Engineering."

    if new_inv["status"] != "awaiting_payment":
        return False, f"New invoice status is '{new_inv['status']}', expected 'awaiting_payment' (approved)."

    if not new_inv.get("sentAt"):
        return False, "New invoice has not been sent."

    return True, f"QU-0024 accepted, converted to {new_inv['number']}, approved and sent."
