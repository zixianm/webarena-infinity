import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that DES-12 has due date 2025-03-15."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    issue = next((i for i in state.get("issues", []) if i.get("identifier") == "DES-12"), None)
    if not issue:
        return False, "Issue DES-12 not found."

    due_date = issue.get("dueDate")
    if due_date != "2025-03-15":
        return False, f"Expected due date '2025-03-15', got '{due_date}'."

    return True, "DES-12 due date is set to 2025-03-15."
