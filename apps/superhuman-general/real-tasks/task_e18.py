import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    provider = state.get("settings", {}).get("meetingLink", {}).get("provider")
    if provider == "google-meet":
        return True, "The meeting link provider has been successfully switched to Google Meet."
    return False, f"The meeting link provider is '{provider}', expected 'google-meet'."
