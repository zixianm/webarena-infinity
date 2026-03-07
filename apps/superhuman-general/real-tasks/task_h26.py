import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    failures = []

    rr = settings.get("readReceipts", {})
    if rr.get("enabled") is not False:
        failures.append(f"Read receipts still enabled (got {rr.get('enabled')})")

    kb = settings.get("keyboard", {})
    if kb.get("shortcuts") is not False:
        failures.append(f"Keyboard shortcuts still enabled (got {kb.get('shortcuts')})")

    swipe_right = settings.get("swipeRight", "")
    if swipe_right != "done":
        failures.append(f"Swipe right is '{swipe_right}', expected 'done' (archive)")

    if failures:
        return False, "; ".join(failures)

    return True, "Read receipts off, keyboard shortcuts off, swipe right set to archive."
