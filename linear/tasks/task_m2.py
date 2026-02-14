import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that a sub-issue 'Write unit tests' exists under ENG-34."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    parent = next((i for i in state.get("issues", []) if i.get("identifier") == "ENG-34"), None)
    if not parent:
        return False, "Parent issue ENG-34 not found."

    sub_issues = [i for i in state.get("issues", [])
                  if i.get("parentIssueId") == parent.get("id") and i.get("title") == "Write unit tests"]
    if not sub_issues:
        return False, "Sub-issue 'Write unit tests' not found under ENG-34."

    return True, "Sub-issue 'Write unit tests' exists under ENG-34."
