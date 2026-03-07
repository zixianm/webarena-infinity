import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])
    if not emails:
        return False, "No emails found in state."

    target_recipient = "sophie.l@eurodesign.fr"
    sender = "alex.morgan@acmecorp.com"

    for email in emails:
        to_field = email.get("to", [])
        # Extract email addresses from to field (list of {name, email} dicts)
        if isinstance(to_field, list):
            recipients = [r.get("email", "").lower() if isinstance(r, dict) else r.lower() for r in to_field]
        else:
            recipients = [to_field.lower() if isinstance(to_field, str) else ""]

        if target_recipient not in recipients:
            continue

        subject = email.get("subject", "")
        if "eurodesign" not in subject.lower():
            continue

        if email.get("isDraft", True):
            return False, (
                f"Found email to {target_recipient} with subject '{subject}' "
                f"but it is still a draft (isDraft=True)."
            )

        return True, (
            f"Draft to Sophie Laurent sent successfully. "
            f"Email to '{target_recipient}' with subject '{subject}' has isDraft=False."
        )

    return False, (
        f"No email found to '{target_recipient}' with subject containing 'EuroDesign'. "
        f"The draft may not have been sent or may have been deleted."
    )
