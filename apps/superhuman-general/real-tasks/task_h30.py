import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    booking_pages = state.get("bookingPages", [])
    failures = []

    # Check Strategy Session exists
    strategy = None
    for bp in booking_pages:
        if bp.get("title", "").strip().lower() == "strategy session":
            strategy = bp
            break

    if strategy is None:
        failures.append("No booking page 'Strategy Session' found.")
    else:
        if strategy.get("duration") != 90:
            failures.append(f"Strategy Session duration is {strategy.get('duration')}, expected 90.")
        loc = strategy.get("location", "")
        if "zoom" not in loc.lower():
            failures.append(f"Strategy Session location is '{loc}', expected Zoom.")
        avail = strategy.get("availability", {})
        days = [d.lower()[:3] for d in avail.get("days", [])]
        expected = {"mon", "tue", "wed", "thu"}
        actual = set(days)
        if not expected.issubset(actual):
            failures.append(f"Strategy Session days missing {expected - actual}. Got: {avail.get('days', [])}")
        if "fri" in actual:
            failures.append("Strategy Session should not include Friday.")
        if avail.get("startTime") != "13:00":
            failures.append(f"Strategy Session startTime is '{avail.get('startTime')}', expected '13:00'.")
        if avail.get("endTime") != "17:00":
            failures.append(f"Strategy Session endTime is '{avail.get('endTime')}', expected '17:00'.")

    # Check Chat with Alex is deactivated
    chat = None
    for bp in booking_pages:
        if bp.get("title", "").strip().lower() == "chat with alex":
            chat = bp
            break
    if chat is None:
        failures.append("Booking page 'Chat with Alex' not found (should exist but be inactive).")
    elif chat.get("isActive") is not False:
        failures.append(f"'Chat with Alex' is still active (isActive={chat.get('isActive')}).")

    if failures:
        return False, "; ".join(failures)

    return True, "Strategy Session booking page created correctly and Chat with Alex deactivated."
