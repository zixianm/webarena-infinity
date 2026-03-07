import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    bp = next((b for b in state["bookingPages"] if b["title"] == "Product Demo"), None)
    if bp:
        return False, "Booking page 'Product Demo' still exists."
    return True, "Booking page 'Product Demo' deleted."
