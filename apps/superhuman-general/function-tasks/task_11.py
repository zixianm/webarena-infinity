import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if "AI Startup Funding Hits Record" in e["subject"]), None)
    if not email:
        return False, "Email about AI Startup Funding not found."
    if not email["isSpam"]:
        return False, "Email is not marked as spam."
    return True, "Email marked as spam."
