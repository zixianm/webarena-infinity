import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify: label group 'Severity' exists, and a 'Critical' label with red color is in that group."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find label group
    group = next((g for g in state.get("labelGroups", []) if g.get("name") == "Severity"), None)
    if not group:
        return False, "Label group 'Severity' not found."

    # Find label 'Critical' in that group
    critical = next((l for l in state.get("labels", [])
                     if l.get("name") == "Critical" and l.get("groupId") == group.get("id")), None)
    if not critical:
        return False, "Label 'Critical' not found in the 'Severity' group."

    color = (critical.get("color") or "").lower()
    red_colors = ["#ef4444", "#dc2626", "#f44336", "#ff0000", "#e53e3e", "#b91c1c", "#991b1b", "red", "#ff4444", "#cc0000"]
    if color not in red_colors:
        return False, f"Expected red color for 'Critical', got '{color}'."

    return True, "Label group 'Severity' with 'Critical' (red) label exists."
