import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the project 'legacy-monolith' has been deleted."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Check that no project named 'legacy-monolith' exists
    match = [p for p in state["projects"] if p["name"] == "legacy-monolith"]
    if match:
        return False, "Project 'legacy-monolith' still exists."

    # Verify that the original project's ID (19) has no lingering memberships
    lingering_memberships = [
        m for m in state["projectMemberships"] if m["projectId"] == 19
    ]
    if lingering_memberships:
        return False, f"Found {len(lingering_memberships)} lingering project membership(s) for deleted project."

    return True, "Project 'legacy-monolith' has been successfully deleted."
