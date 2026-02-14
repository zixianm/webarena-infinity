import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify: 'Upgrade database driver' (High, ENG) blocks ENG-38, related to ENG-39."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    issue = next((i for i in state.get("issues", []) if i.get("title") == "Upgrade database driver"), None)
    if not issue:
        return False, "Issue 'Upgrade database driver' not found."

    errors = []

    if issue.get("teamId") != "team-1":
        errors.append(f"Expected team 'team-1' (Engineering), got '{issue.get('teamId')}'.")

    priority = issue.get("priority", {})
    pname = priority.get("name", "") if isinstance(priority, dict) else str(priority)
    if pname != "High":
        errors.append(f"Expected priority 'High', got '{pname}'.")

    issue_id = issue.get("id")
    eng38 = next((i for i in state.get("issues", []) if i.get("identifier") == "ENG-38"), None)
    eng39 = next((i for i in state.get("issues", []) if i.get("identifier") == "ENG-39"), None)

    if not eng38:
        errors.append("ENG-38 not found.")
    if not eng39:
        errors.append("ENG-39 not found.")

    relations = state.get("issueRelations", [])

    # Check blocks ENG-38
    if eng38:
        blocking = [r for r in relations
                    if r.get("issueId") == issue_id
                    and r.get("relatedIssueId") == eng38.get("id")
                    and r.get("type") == "blocks"]
        if not blocking:
            errors.append("No 'blocks' relation from new issue to ENG-38.")

    # Check related to ENG-39
    if eng39:
        related = [r for r in relations
                   if (r.get("issueId") == issue_id and r.get("relatedIssueId") == eng39.get("id") and r.get("type") == "related") or
                      (r.get("issueId") == eng39.get("id") and r.get("relatedIssueId") == issue_id and r.get("type") == "related")]
        if not related:
            errors.append("No 'related' relation between new issue and ENG-39.")

    if errors:
        return False, " | ".join(errors)

    return True, "Issue created with both relations correctly."
