import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that CS-22 was deleted then restored (deletedAt should be null, updatedAt should have changed)."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    issue = next((i for i in state.get("issues", []) if i.get("identifier") == "CS-22"), None)
    if not issue:
        return False, "Issue CS-22 not found."

    if issue.get("deletedAt") is not None:
        return False, f"CS-22 still has deletedAt set to '{issue.get('deletedAt')}'. It should be null (restored)."

    # Check that updatedAt changed from the original seed value, indicating the issue was modified
    original_updated = "2025-01-26T08:00:00Z"
    if issue.get("updatedAt") == original_updated:
        return False, "CS-22 updatedAt has not changed from seed value. The issue needs to be deleted then restored."

    return True, "CS-22 was deleted and restored (deletedAt is null, updatedAt changed)."
