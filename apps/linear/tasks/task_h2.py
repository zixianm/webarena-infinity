import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify: label group 'Environment' with 'Staging' (orange) and 'Production' (red), Production applied to ENG-34."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Check label group
    group = next((g for g in state.get("labelGroups", []) if g.get("name") == "Environment"), None)
    if not group:
        return False, "Label group 'Environment' not found."
    group_id = group.get("id")

    # Check Staging label
    staging = next((l for l in state.get("labels", [])
                    if l.get("name") == "Staging" and l.get("groupId") == group_id), None)
    if not staging:
        errors.append("Label 'Staging' not found in 'Environment' group.")
    else:
        color = (staging.get("color") or "").lower()
        orange_colors = ["#f97316", "#f59e0b", "#ff9800", "#fb923c", "#ea580c", "#d97706", "orange"]
        if color not in orange_colors:
            errors.append(f"Expected orange color for 'Staging', got '{color}'.")

    # Check Production label
    production = next((l for l in state.get("labels", [])
                       if l.get("name") == "Production" and l.get("groupId") == group_id), None)
    if not production:
        errors.append("Label 'Production' not found in 'Environment' group.")
    else:
        color = (production.get("color") or "").lower()
        red_colors = ["#ef4444", "#dc2626", "#f44336", "#ff0000", "#e53e3e", "#b91c1c", "red"]
        if color not in red_colors:
            errors.append(f"Expected red color for 'Production', got '{color}'.")

    # Check ENG-34 has Production label
    eng34 = next((i for i in state.get("issues", []) if i.get("identifier") == "ENG-34"), None)
    if not eng34:
        errors.append("Issue ENG-34 not found.")
    elif production and production.get("id") not in eng34.get("labelIds", []):
        errors.append("ENG-34 does not have the 'Production' label.")

    if errors:
        return False, " | ".join(errors)

    return True, "Environment group, Staging, Production labels created; Production applied to ENG-34."
