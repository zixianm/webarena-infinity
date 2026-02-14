import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify: issue 'Redesign settings page' in Design, Medium priority, assigned to Emma Wilson, 'Improvement' label."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    match = [i for i in state.get("issues", []) if i.get("title") == "Redesign settings page"]
    if not match:
        return False, "Issue 'Redesign settings page' not found."

    issue = match[0]
    errors = []

    # Team check
    if issue.get("teamId") != "team-2":
        errors.append(f"Expected team 'team-2' (Design), got '{issue.get('teamId')}'.")

    # Priority check
    priority = issue.get("priority", {})
    pname = priority.get("name", "") if isinstance(priority, dict) else str(priority)
    if pname != "Medium":
        errors.append(f"Expected priority 'Medium', got '{pname}'.")

    # Assignee check
    assignee_id = issue.get("assigneeId")
    if assignee_id:
        user = next((u for u in state.get("users", []) if u.get("id") == assignee_id), None)
        if not user or user.get("name") != "Emma Wilson":
            errors.append(f"Expected assignee 'Emma Wilson', got '{user.get('name') if user else 'unknown'}'.")
    else:
        errors.append("Issue has no assignee.")

    # Label check
    label_ids = issue.get("labelIds", [])
    improvement_label = next((l for l in state.get("labels", []) if l.get("name") == "Improvement"), None)
    if not improvement_label or improvement_label.get("id") not in label_ids:
        errors.append("Issue does not have the 'Improvement' label.")

    if errors:
        return False, " | ".join(errors)

    return True, "Issue 'Redesign settings page' created correctly with all properties."
