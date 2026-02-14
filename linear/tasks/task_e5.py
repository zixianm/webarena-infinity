import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify that ENG-36 has the 'Bug' label."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    issue = next((i for i in state.get("issues", []) if i.get("identifier") == "ENG-36"), None)
    if not issue:
        return False, "Issue ENG-36 not found."

    label_ids = issue.get("labelIds", [])
    bug_label = next((l for l in state.get("labels", []) if l.get("name") == "Bug"), None)
    if not bug_label:
        return False, "Bug label not found in state."

    if bug_label.get("id") not in label_ids:
        return False, f"ENG-36 does not have the 'Bug' label. Current labels: {label_ids}"

    return True, "ENG-36 has the 'Bug' label."
