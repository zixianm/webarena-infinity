import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    read_receipts = state.get("settings", {}).get("readReceipts", {})
    enabled = read_receipts.get("enabled")
    if enabled is False:
        return True, "Read receipts are disabled."
    return False, f"Expected read receipts enabled to be False, but got {enabled!r}."
