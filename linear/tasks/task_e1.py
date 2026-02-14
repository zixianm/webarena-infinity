import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that a new issue 'Fix login page timeout' exists in Engineering with High priority."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    match = [i for i in state.get("issues", []) if i.get("title") == "Fix login page timeout"]
    if not match:
        return False, "Issue 'Fix login page timeout' not found."

    issue = match[0]

    if issue.get("teamId") != "team-1":
        return False, f"Issue is in team '{issue.get('teamId')}', expected 'team-1' (Engineering)."

    priority = issue.get("priority", {})
    if isinstance(priority, dict):
        pname = priority.get("name", "")
    else:
        pname = str(priority)
    if pname != "High":
        return False, f"Expected priority 'High', got '{pname}'."

    return True, "Issue 'Fix login page timeout' created in Engineering with High priority."
