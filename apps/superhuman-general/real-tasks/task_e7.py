import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    snippets = state.get("snippets", [])
    for snippet in snippets:
        name = snippet.get("name", "")
        if name == "Decline Politely":
            return False, "The 'Decline Politely' snippet still exists."

    return True, "The 'Decline Politely' snippet has been deleted."
