import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    target_subject = "Partnership Opportunity - FinancePlus x Acme"
    target_sender = "david.kim@financeplus.com"

    emails = state.get("emails", [])
    for email in emails:
        sender = email.get("from") or email.get("sender") or email.get("senderEmail", "")
        subject = email.get("subject", "")
        if subject == target_subject or sender == target_sender:
            if email.get("isStarred") is True:
                return True, "The email from David Kim about the FinancePlus partnership is starred."
            return False, f"Found the email but isStarred is {email.get('isStarred')!r}, expected True."

    return False, f"Could not find email with subject '{target_subject}' from '{target_sender}'."
