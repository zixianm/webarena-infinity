import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    drafts = [e for e in state["emails"] if e["subject"] == "Integration Discussion" and e.get("isDraft")]
    if not drafts:
        return False, "Draft 'Integration Discussion' not found."
    draft = drafts[0]
    to_emails = [t["email"] for t in draft.get("to", [])]
    if "kevin.zhao@quantumlab.tech" not in to_emails:
        return False, f"Draft not addressed to kevin.zhao@quantumlab.tech. To: {to_emails}"
    body = draft.get("body", "")
    if "quantum" not in body.lower() or "integration" not in body.lower() or "prototype" not in body.lower():
        return False, f"Draft body does not match expected content."
    return True, "Draft saved with correct recipient, subject and body."
