import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    settings = state.get("settings", {})
    section = settings.get("meetingLink", {})
    val = section.get("provider")
    if val != "google-meet":
        return False, f"Meeting link provider: expected 'google-meet', got '{val}'"
    return True, "Meeting link provider set to 'google-meet'."
