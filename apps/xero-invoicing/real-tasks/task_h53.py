import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # QU-0028 (Metro Fabrication Works) should be declined
    old_quo = next((q for q in state["quotes"] if q["number"] == "QU-0028"), None)
    if not old_quo:
        return False, "Quote QU-0028 not found."
    if old_quo["status"] != "declined":
        return False, f"QU-0028 status is '{old_quo['status']}', expected 'declined'."

    # Find a new sent quote for Metro Fabrication with Widget B
    contact = next((c for c in state["contacts"] if c["name"] == "Metro Fabrication Works"), None)
    if not contact:
        return False, "Metro Fabrication Works contact not found."

    new_quo = next((q for q in state["quotes"]
                    if q["contactId"] == contact["id"]
                    and q["status"] == "sent"
                    and q["number"] != "QU-0028"
                    and any(li.get("itemId") == "item_012" for li in q.get("lineItems", []))), None)

    if not new_quo:
        return False, "No new sent quote with Widget B found for Metro Fabrication Works."

    widget_line = next((li for li in new_quo["lineItems"] if li.get("itemId") == "item_012"), None)
    if widget_line["quantity"] != 5:
        return False, f"Widget B quantity is {widget_line['quantity']}, expected 5."

    return True, f"QU-0028 declined, new quote {new_quo['number']} sent with 5 Widget B."
