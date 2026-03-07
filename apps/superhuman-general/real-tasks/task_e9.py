import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    smart_send = state.get("settings", {}).get("smartSend", {})
    enabled = smart_send.get("enabled")
    if enabled is False:
        return True, "Smart Send is disabled."
    return False, f"Expected Smart Send enabled to be False, but got {enabled!r}."
