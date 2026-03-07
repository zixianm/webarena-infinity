import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    bp = next((b for b in state["bookingPages"] if b["title"] == "Strategy Session"), None)
    if not bp:
        return False, "Booking page 'Strategy Session' not found."
    if bp["duration"] != 60:
        return False, f"Duration should be 60, got {bp['duration']}."
    if bp.get("location", "").lower() != "zoom":
        return False, f"Location should be 'Zoom', got '{bp.get('location', '')}'."
    return True, "Booking page 'Strategy Session' created with correct details."
