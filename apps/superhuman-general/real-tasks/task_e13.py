import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    booking_pages = state.get("bookingPages", [])
    for page in booking_pages:
        if page.get("title") == "Product Demo":
            return False, "The 'Product Demo' booking page still exists."
    return True, "The 'Product Demo' booking page has been successfully deleted."
