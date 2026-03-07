import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    split = next((s for s in state["splits"] if s["name"] == "Feeds"), None)
    if split:
        return False, "Split 'Feeds' still exists."
    return True, "Split 'Feeds' deleted."
