import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that CS-20 is deleted (deletedAt is not null)."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    issue = next((i for i in state.get("issues", []) if i.get("identifier") == "CS-20"), None)
    if not issue:
        return False, "Issue CS-20 not found."

    if not issue.get("deletedAt"):
        return False, "CS-20 is not deleted (deletedAt is null)."

    return True, "CS-20 has been deleted."
