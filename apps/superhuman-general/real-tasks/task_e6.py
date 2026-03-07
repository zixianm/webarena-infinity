import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    target_subject = "Logistics Update - Office Equipment Delivery"
    target_sender = "carlos.m@logisticspro.net"

    emails = state.get("emails", [])
    for email in emails:
        sender = email.get("from") or email.get("sender") or email.get("senderEmail", "")
        subject = email.get("subject", "")
        if subject == target_subject or sender == target_sender:
            if email.get("isTrashed") is True:
                return True, "The email about office equipment delivery from Carlos is trashed."
            return False, f"Found the email but isTrashed is {email.get('isTrashed')!r}, expected True."

    return False, f"Could not find email with subject '{target_subject}' from '{target_sender}'."
