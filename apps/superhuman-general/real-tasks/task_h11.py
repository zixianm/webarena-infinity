import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    booking_pages = state.get("bookingPages", [])
    if not booking_pages:
        return False, "No booking pages found in state."

    match = None
    for page in booking_pages:
        if page.get("title", "").strip().lower() == "office hours":
            match = page
            break

    if not match:
        titles = [p.get("title", "") for p in booking_pages]
        return False, f"No booking page with title 'Office Hours' found. Existing titles: {titles}"

    if match.get("duration") != 60:
        return False, f"Expected duration 60, got {match.get('duration')}."

    location = match.get("location", "")
    if "google meet" not in location.lower():
        return False, f"Expected location containing 'Google Meet', got '{location}'."

    availability = match.get("availability", {})
    start_time = availability.get("startTime", "")
    end_time = availability.get("endTime", "")

    if start_time != "14:00":
        return False, f"Expected availability startTime '14:00', got '{start_time}'."

    if end_time != "17:00":
        return False, f"Expected availability endTime '17:00', got '{end_time}'."

    days = availability.get("days", [])
    # Accept both full names and abbreviations
    day_map = {"mon": "monday", "tue": "tuesday", "wed": "wednesday", "thu": "thursday", "fri": "friday",
               "monday": "monday", "tuesday": "tuesday", "wednesday": "wednesday", "thursday": "thursday", "friday": "friday"}
    expected_days = {"monday", "tuesday", "wednesday", "thursday", "friday"}
    actual_days = {day_map.get(d.lower(), d.lower()) for d in days}
    if not expected_days.issubset(actual_days):
        missing = expected_days - actual_days
        return False, f"Expected availability Monday-Friday. Missing days: {missing}. Got: {days}"

    return True, "Booking page 'Office Hours' created correctly with 60min duration, Google Meet, Mon-Fri 2pm-5pm."
