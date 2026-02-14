import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that PRD-10 has Urgent priority."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    issue = next((i for i in state.get("issues", []) if i.get("identifier") == "PRD-10"), None)
    if not issue:
        return False, "Issue PRD-10 not found."

    priority = issue.get("priority", {})
    if isinstance(priority, dict):
        pname = priority.get("name", "")
    else:
        pname = str(priority)
    if pname != "Urgent":
        return False, f"Expected priority 'Urgent', got '{pname}'."

    return True, "PRD-10 priority is Urgent."
