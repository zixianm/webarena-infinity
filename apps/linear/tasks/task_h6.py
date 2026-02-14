import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify: 'Implement caching layer' (Medium, ENG), assigned to Yuki, project Q1 Launch, cycle Sprint 13."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    issue = next((i for i in state.get("issues", []) if i.get("title") == "Implement caching layer"), None)
    if not issue:
        return False, "Issue 'Implement caching layer' not found."

    errors = []

    if issue.get("teamId") != "team-1":
        errors.append(f"Expected team 'team-1' (Engineering), got '{issue.get('teamId')}'.")

    priority = issue.get("priority", {})
    pname = priority.get("name", "") if isinstance(priority, dict) else str(priority)
    if pname != "Medium":
        errors.append(f"Expected priority 'Medium', got '{pname}'.")

    # Assignee = Yuki Tanaka
    assignee_id = issue.get("assigneeId")
    if assignee_id:
        user = next((u for u in state.get("users", []) if u.get("id") == assignee_id), None)
        if not user or user.get("name") != "Yuki Tanaka":
            errors.append(f"Expected assignee 'Yuki Tanaka', got '{user.get('name') if user else 'unknown'}'.")
    else:
        errors.append("Issue has no assignee.")

    # Project = Q1 Launch
    project_id = issue.get("projectId")
    if project_id:
        project = next((p for p in state.get("projects", []) if p.get("id") == project_id), None)
        if not project or project.get("name") != "Q1 Launch":
            errors.append(f"Expected project 'Q1 Launch', got '{project.get('name') if project else 'unknown'}'.")
    else:
        errors.append("Issue has no project.")

    # Cycle = Sprint 13
    cycle_id = issue.get("cycleId")
    if cycle_id:
        cycle = next((c for c in state.get("cycles", []) if c.get("id") == cycle_id), None)
        if not cycle or cycle.get("name") != "Sprint 13":
            errors.append(f"Expected cycle 'Sprint 13', got '{cycle.get('name') if cycle else 'unknown'}'.")
    else:
        errors.append("Issue has no cycle.")

    if errors:
        return False, " | ".join(errors)

    return True, "Issue created with all four properties correctly."
