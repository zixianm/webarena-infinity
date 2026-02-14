import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Design team has estimates enabled with T-Shirt scale."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    team = next((t for t in state.get("teams", []) if t.get("id") == "team-2"), None)
    if not team:
        return False, "Design team (team-2) not found."

    settings = team.get("settings", {})
    errors = []

    if not settings.get("estimatesEnabled"):
        errors.append("Estimates are not enabled.")

    scale = settings.get("estimateScale", "")
    if scale != "T-Shirt":
        errors.append(f"Expected estimate scale 'T-Shirt', got '{scale}'.")

    if errors:
        return False, " | ".join(errors)

    return True, "Design team has estimates enabled with T-Shirt scale."
