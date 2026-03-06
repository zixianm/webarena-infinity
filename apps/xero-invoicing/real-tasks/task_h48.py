import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    settings = state.get("invoiceSettings", {})

    due_date = settings.get("defaultDueDate", {})
    if due_date.get("type") != "endOfFollowingMonth":
        return False, f"Default due date type is '{due_date.get('type')}', expected 'endOfFollowingMonth'."

    quote_num = settings.get("quoteNextNumber")
    if quote_num != 50:
        return False, f"Quote next number is {quote_num}, expected 50."

    return True, "Default due date set to end of following month, quote numbering starts at 50."
