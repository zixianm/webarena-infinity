import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that ENG-38 blocks ENG-39."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    eng38 = next((i for i in state.get("issues", []) if i.get("identifier") == "ENG-38"), None)
    eng39 = next((i for i in state.get("issues", []) if i.get("identifier") == "ENG-39"), None)
    if not eng38 or not eng39:
        return False, "ENG-38 or ENG-39 not found."

    # Check for a 'blocks' relation from ENG-38 to ENG-39
    relations = state.get("issueRelations", [])
    blocking = [r for r in relations
                if r.get("issueId") == eng38.get("id")
                and r.get("relatedIssueId") == eng39.get("id")
                and r.get("type") == "blocks"]
    if not blocking:
        return False, "No 'blocks' relation found from ENG-38 to ENG-39."

    return True, "ENG-38 is marked as blocking ENG-39."
