import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that DES-14 has a comment 'The mockups look great, approved for development.'"""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    issue = next((i for i in state.get("issues", []) if i.get("identifier") == "DES-14"), None)
    if not issue:
        return False, "Issue DES-14 not found."

    comments = [c for c in state.get("comments", []) if c.get("issueId") == issue.get("id")]
    target_text = "The mockups look great, approved for development."
    match = [c for c in comments if target_text in (c.get("body") or "")]
    if not match:
        return False, f"Comment '{target_text}' not found on DES-14. Found {len(comments)} comments."

    return True, "Comment found on DES-14."
