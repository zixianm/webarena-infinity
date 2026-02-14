import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify: template 'Performance Issue' (High) exists, and issue 'Optimize API response times' created from it."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Check template exists
    template = next((t for t in state.get("templates", []) if t.get("name") == "Performance Issue"), None)
    if not template:
        errors.append("Template 'Performance Issue' not found.")
    else:
        tp = template.get("defaultPriority", {})
        tpname = tp.get("name", "") if isinstance(tp, dict) else str(tp)
        if tpname != "High":
            errors.append(f"Expected template default priority 'High', got '{tpname}'.")

    # Check issue exists
    issue = next((i for i in state.get("issues", []) if i.get("title") == "Optimize API response times"), None)
    if not issue:
        errors.append("Issue 'Optimize API response times' not found.")
    else:
        # Verify it has High priority (from template)
        priority = issue.get("priority", {})
        pname = priority.get("name", "") if isinstance(priority, dict) else str(priority)
        if pname != "High":
            errors.append(f"Expected issue priority 'High' (from template), got '{pname}'.")

        if issue.get("teamId") != "team-1":
            errors.append(f"Expected team 'team-1' (Engineering), got '{issue.get('teamId')}'.")

    if errors:
        return False, " | ".join(errors)

    return True, "Template 'Performance Issue' and issue created from it exist correctly."
