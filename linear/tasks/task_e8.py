import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that a workspace label 'Regression' with red color exists."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    match = [l for l in state.get("labels", []) if l.get("name") == "Regression"]
    if not match:
        return False, "Label 'Regression' not found."

    label = match[0]
    if label.get("scope") != "workspace":
        return False, f"Expected scope 'workspace', got '{label.get('scope')}'."

    color = (label.get("color") or "").lower()
    red_colors = ["#ef4444", "#dc2626", "#f44336", "#ff0000", "#e53e3e", "#b91c1c", "#991b1b", "red", "#ff4444", "#cc0000"]
    if color not in red_colors:
        return False, f"Expected a red color, got '{color}'."

    return True, "Workspace label 'Regression' with red color exists."
