import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    instant_reply = state.get("settings", {}).get("instantReply", {})
    enabled = instant_reply.get("enabled")
    if enabled is False:
        return True, "Instant Reply is disabled."
    return False, f"Expected Instant Reply enabled to be False, but got {enabled!r}."
