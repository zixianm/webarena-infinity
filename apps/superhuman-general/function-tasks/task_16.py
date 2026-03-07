import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sent = [e for e in state["emails"] if e["subject"] == "Design Review Follow-up" and e["from"]["email"] == "alex.morgan@acmecorp.com"]
    if not sent:
        return False, "Sent email 'Design Review Follow-up' not found."
    email = sent[0]
    to_emails = [t["email"] for t in email.get("to", [])]
    if "marcus.w@designhub.io" not in to_emails:
        return False, f"Email not sent to marcus.w@designhub.io. To: {to_emails}"
    if email.get("isDraft"):
        return False, "Email is still a draft, not sent."
    body = email.get("body", "")
    if "design review" not in body.lower() or "components" not in body.lower():
        return False, f"Email body does not match expected content."
    return True, "Email sent to marcus.w@designhub.io with correct subject and body."
