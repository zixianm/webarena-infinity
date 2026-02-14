import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that ENG-34 has status 'Done'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    issue = next((i for i in state.get("issues", []) if i.get("identifier") == "ENG-34"), None)
    if not issue:
        return False, "Issue ENG-34 not found."

    status_id = issue.get("statusId")
    # Find the status name from the team's statuses
    team = next((t for t in state.get("teams", []) if t.get("id") == issue.get("teamId")), None)
    if not team:
        return False, "Team for ENG-34 not found."

    status = next((s for s in team.get("statuses", []) if s.get("id") == status_id), None)
    if not status:
        return False, f"Status with id '{status_id}' not found in team."

    if status.get("name") != "Done":
        return False, f"Expected status 'Done', got '{status.get('name')}'."

    return True, "ENG-34 status is 'Done'."
