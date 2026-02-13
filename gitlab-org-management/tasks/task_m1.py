import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that project 'monitoring-service' was created in the Observability group."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Find the Observability group
    obs_group = next(
        (g for g in state["groups"] if g["name"] == "Observability"), None
    )
    if not obs_group:
        return False, "Observability group not found."

    # Find the project
    match = [p for p in state["projects"] if p["name"] == "monitoring-service"]
    if not match:
        return False, "Project 'monitoring-service' not found."

    project = match[0]
    if project.get("groupId") != obs_group["id"]:
        actual_group = next(
            (g for g in state["groups"] if g["id"] == project.get("groupId")), None
        )
        actual_name = actual_group["name"] if actual_group else "unknown"
        return False, f"Project is in group '{actual_name}', expected 'Observability'."

    return True, "Project 'monitoring-service' created in the Observability group."
