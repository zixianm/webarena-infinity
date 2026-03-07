import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    snippet = next((s for s in state["snippets"] if s["name"] == "[Sales] Product Demo"), None)
    if not snippet:
        return False, "Snippet '[Sales] Product Demo' not found."
    if snippet["isShared"]:
        return False, "Snippet '[Sales] Product Demo' is still shared."
    return True, "Snippet '[Sales] Product Demo' is now private."
