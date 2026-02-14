import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that ENG-40 was moved to Product team (new identifier should start with PRD-)."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # The issue was originally ENG-40 with title 'Implement feature flags system'
    # After move, it should have teamId='team-3' and identifier starting with 'PRD-'
    match = [i for i in state.get("issues", []) if i.get("title") == "Implement feature flags system"]
    if not match:
        return False, "Issue 'Implement feature flags system' (originally ENG-40) not found."

    issue = match[0]

    if issue.get("teamId") != "team-3":
        return False, f"Expected teamId 'team-3' (Product), got '{issue.get('teamId')}'."

    identifier = issue.get("identifier", "")
    if not identifier.startswith("PRD-"):
        return False, f"Expected identifier to start with 'PRD-', got '{identifier}'."

    return True, f"Issue moved to Product team with identifier {identifier}."
