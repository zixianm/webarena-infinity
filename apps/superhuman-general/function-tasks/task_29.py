import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    bp = next((b for b in state["bookingPages"] if b["title"] == "Quick Sync"), None)
    if not bp:
        return False, "Booking page 'Quick Sync' not found."
    if not bp["isActive"]:
        return False, "Booking page 'Quick Sync' is not active."
    return True, "Booking page 'Quick Sync' is now active."
