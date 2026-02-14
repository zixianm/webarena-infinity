import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify web-frontend project settings: name, description, topics, visibility."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # web-frontend is project ID 6
    project = next((p for p in state["projects"] if p["id"] == 6), None)
    if not project:
        # Maybe renamed — search by new name
        project = next(
            (p for p in state["projects"] if p["name"] == "web-app-frontend"), None
        )
        if not project:
            return False, "Project id=6 not found, nor a project named 'web-app-frontend'."

    errors = []

    # Check name
    if project.get("name") != "web-app-frontend":
        errors.append(f"name: expected 'web-app-frontend', got '{project.get('name')}'")

    # Check description
    expected_desc = "Main customer-facing web application"
    if project.get("description") != expected_desc:
        errors.append(f"description: expected '{expected_desc}', got '{project.get('description')}'")

    # Check topics
    expected_topics = sorted(["react", "vue", "frontend"])
    actual_topics = sorted(project.get("topics", []))
    if actual_topics != expected_topics:
        errors.append(f"topics: expected {expected_topics}, got {actual_topics}")

    # Check visibility
    if project.get("visibility") != "private":
        errors.append(f"visibility: expected 'private', got '{project.get('visibility')}'")

    if errors:
        return False, "Settings check failed: " + "; ".join(errors)

    return True, "web-frontend project settings all updated correctly."
