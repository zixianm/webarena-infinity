import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify: 'Implement OAuth2 authentication' (High, ENG) + 2 sub-issues."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    parent = next((i for i in state.get("issues", [])
                   if i.get("title") == "Implement OAuth2 authentication"), None)
    if not parent:
        return False, "Issue 'Implement OAuth2 authentication' not found."

    if parent.get("teamId") != "team-1":
        return False, f"Expected team 'team-1' (Engineering), got '{parent.get('teamId')}'."

    priority = parent.get("priority", {})
    pname = priority.get("name", "") if isinstance(priority, dict) else str(priority)
    if pname != "High":
        return False, f"Expected priority 'High', got '{pname}'."

    # Check sub-issues
    parent_id = parent.get("id")
    sub_issues = [i for i in state.get("issues", []) if i.get("parentIssueId") == parent_id]

    expected_titles = {"Set up OAuth2 provider", "Implement token refresh flow"}
    found_titles = {i.get("title") for i in sub_issues}

    missing = expected_titles - found_titles
    if missing:
        return False, f"Missing sub-issues: {missing}. Found: {found_titles}"

    return True, "Parent issue and both sub-issues created correctly."
