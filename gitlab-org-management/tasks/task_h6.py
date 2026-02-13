import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Observability group settings: name, subgroup creation, project creation, disable mentions."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Observability is group ID 8
    group = next((g for g in state["groups"] if g["id"] == 8), None)
    if not group:
        # Maybe renamed — search by new name
        group = next(
            (g for g in state["groups"] if g["name"] == "Monitoring & Observability"),
            None,
        )
        if not group:
            return False, "Observability group (id=8) not found, nor a group named 'Monitoring & Observability'."

    errors = []

    # Check name
    if group.get("name") != "Monitoring & Observability":
        errors.append(f"name: expected 'Monitoring & Observability', got '{group.get('name')}'")

    # Check subgroup creation setting
    if group.get("subgroupCreation") != "owners":
        errors.append(f"subgroupCreation: expected 'owners', got '{group.get('subgroupCreation')}'")

    # Check project creation setting
    if group.get("projectCreation") != "noone":
        errors.append(f"projectCreation: expected 'noone', got '{group.get('projectCreation')}'")

    # Check disable mentions
    if group.get("disableMentions") is not True:
        errors.append(f"disableMentions: expected true, got '{group.get('disableMentions')}'")

    if errors:
        return False, "Settings check failed: " + "; ".join(errors)

    return True, "Observability group settings all updated correctly."
