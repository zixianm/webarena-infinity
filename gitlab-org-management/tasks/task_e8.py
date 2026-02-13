import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that status message is 'On vacation' and busy is true."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    current_user = state.get("currentUser", {})
    status = current_user.get("status", {})

    if status.get("message") != "On vacation":
        return False, f"Expected status message 'On vacation', got '{status.get('message')}'."

    if status.get("busy") is not True:
        return False, f"Expected busy=true, got '{status.get('busy')}'."

    return True, "Status message set to 'On vacation' and busy is enabled."
