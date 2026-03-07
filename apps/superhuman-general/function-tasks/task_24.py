import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    snippet = next((s for s in state["snippets"] if s["name"] == "Scheduling Request"), None)
    if not snippet:
        return False, "Snippet 'Scheduling Request' not found."
    if not snippet["isShared"]:
        return False, "Snippet 'Scheduling Request' is not shared."
    return True, "Snippet 'Scheduling Request' is now shared."
