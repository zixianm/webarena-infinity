import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    snippet = next((s for s in state["snippets"] if s["name"] == "Decline Politely"), None)
    if snippet:
        return False, "Snippet 'Decline Politely' still exists."
    return True, "Snippet 'Decline Politely' deleted."
