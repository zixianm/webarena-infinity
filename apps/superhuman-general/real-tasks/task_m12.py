import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    secondary_tz = settings.get("secondaryTimezone")

    if secondary_tz is None or secondary_tz == "" or secondary_tz == "none":
        return True, "Secondary timezone has been successfully removed."

    return False, f"Expected secondary timezone to be empty/none, but found '{secondary_tz}'."
