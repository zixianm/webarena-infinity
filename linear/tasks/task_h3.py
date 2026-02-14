import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify: 'Database migration script' in ENG, Priya, Urgent, Backend label, comment 'Critical for Q1 release'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    match = [i for i in state.get("issues", []) if i.get("title") == "Database migration script"]
    if not match:
        return False, "Issue 'Database migration script' not found."

    issue = match[0]
    errors = []

    # Team
    if issue.get("teamId") != "team-1":
        errors.append(f"Expected team 'team-1' (Engineering), got '{issue.get('teamId')}'.")

    # Assignee = Priya Sharma
    assignee_id = issue.get("assigneeId")
    if assignee_id:
        user = next((u for u in state.get("users", []) if u.get("id") == assignee_id), None)
        if not user or user.get("name") != "Priya Sharma":
            errors.append(f"Expected assignee 'Priya Sharma', got '{user.get('name') if user else 'unknown'}'.")
    else:
        errors.append("Issue has no assignee.")

    # Priority = Urgent
    priority = issue.get("priority", {})
    pname = priority.get("name", "") if isinstance(priority, dict) else str(priority)
    if pname != "Urgent":
        errors.append(f"Expected priority 'Urgent', got '{pname}'.")

    # Backend label
    label_ids = issue.get("labelIds", [])
    backend_label = next((l for l in state.get("labels", []) if l.get("name") == "Backend"), None)
    if not backend_label or backend_label.get("id") not in label_ids:
        errors.append("Issue does not have the 'Backend' label.")

    # Comment
    issue_id = issue.get("id")
    comments = [c for c in state.get("comments", []) if c.get("issueId") == issue_id]
    target = "Critical for Q1 release"
    has_comment = any(target in (c.get("body") or "") for c in comments)
    if not has_comment:
        errors.append(f"Comment '{target}' not found.")

    if errors:
        return False, " | ".join(errors)

    return True, "Issue 'Database migration script' created with all properties and comment."
