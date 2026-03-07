import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    target_subject = "Q2 Product Roadmap - Final Review"
    target_sender = "sarah.chen@acmecorp.com"

    emails = state.get("emails", [])
    for email in emails:
        sender = email.get("from") or email.get("sender") or email.get("senderEmail", "")
        subject = email.get("subject", "")
        if subject == target_subject or sender == target_sender:
            if email.get("isDone") is True:
                return True, "Sarah Chen's Q2 roadmap email is archived (isDone is True)."
            return False, f"Found the email but isDone is {email.get('isDone')!r}, expected True."

    return False, f"Could not find email with subject '{target_subject}' from '{target_sender}'."
