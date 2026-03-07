import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    booking_pages = state.get("bookingPages", [])
    for page in booking_pages:
        if page.get("title") == "Quick Sync":
            if page.get("isActive") is True:
                return True, "The 'Quick Sync' booking page is now active."
            else:
                return False, "The 'Quick Sync' booking page was found but is not active."
    return False, "No booking page with title 'Quick Sync' was found."
