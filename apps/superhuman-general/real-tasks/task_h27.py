import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    booking_pages = state.get("bookingPages", [])

    for bp in booking_pages:
        if bp.get("title", "").lower() == "quick sync":
            return False, "Booking page 'Quick Sync' (15 min, shortest duration) still exists."

    if not booking_pages:
        return False, "All booking pages were deleted — only the shortest should have been removed."

    return True, "Booking page with shortest duration ('Quick Sync', 15 min) has been deleted."
