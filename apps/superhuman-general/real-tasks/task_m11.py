import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    timezone = settings.get("timezone")

    if timezone == "America/Los_Angeles":
        return True, "Primary timezone is correctly set to Pacific Time (America/Los_Angeles)."

    return False, f"Expected timezone 'America/Los_Angeles', but found '{timezone}'."
