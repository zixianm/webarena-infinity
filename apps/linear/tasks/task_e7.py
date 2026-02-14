import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that ENG-37 has estimate of 5."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    issue = next((i for i in state.get("issues", []) if i.get("identifier") == "ENG-37"), None)
    if not issue:
        return False, "Issue ENG-37 not found."

    estimate = issue.get("estimate")
    if estimate != 5:
        return False, f"Expected estimate 5, got {estimate}."

    return True, "ENG-37 estimate is 5 points."
