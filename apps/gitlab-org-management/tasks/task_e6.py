import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the 'Archived Projects' group has been unarchived."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    match = [g for g in state["groups"] if g["name"] == "Archived Projects"]
    if not match:
        return False, "Group 'Archived Projects' not found."

    group = match[0]
    if group.get("archived") is not False:
        return False, f"Group 'Archived Projects' is still archived (archived={group.get('archived')})."

    return True, "Group 'Archived Projects' successfully unarchived."
