import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that ENG-35 is assigned to James Chen."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    issue = next((i for i in state.get("issues", []) if i.get("identifier") == "ENG-35"), None)
    if not issue:
        return False, "Issue ENG-35 not found."

    assignee_id = issue.get("assigneeId")
    if not assignee_id:
        return False, "ENG-35 has no assignee."

    user = next((u for u in state.get("users", []) if u.get("id") == assignee_id), None)
    if not user:
        return False, f"Assignee with id '{assignee_id}' not found in users."

    if user.get("name") != "James Chen":
        return False, f"Expected assignee 'James Chen', got '{user.get('name')}'."

    return True, "ENG-35 is assigned to James Chen."
