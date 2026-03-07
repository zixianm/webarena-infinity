import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])
    target_recipient = "sophie.l@eurodesign.fr"
    sender = "alex.morgan@acmecorp.com"

    # Look for a sent (non-draft) email to Sophie Laurent
    matching_emails = []
    for email in emails:
        from_email = email.get("from", {}).get("email", "")
        to_field = email.get("to", [])
        is_draft = email.get("isDraft", False)

        # Check if addressed to sophie.l@eurodesign.fr
        to_emails = []
        if isinstance(to_field, list):
            for recipient in to_field:
                if isinstance(recipient, dict):
                    to_emails.append(recipient.get("email", ""))
                elif isinstance(recipient, str):
                    to_emails.append(recipient)
        elif isinstance(to_field, str):
            to_emails.append(to_field)

        if target_recipient in to_emails and not is_draft:
            matching_emails.append(email)

    if not matching_emails:
        # Also check if the existing draft (email 73) was sent
        for email in emails:
            eid = email.get("id")
            if eid == 73 or eid == "73":
                if not email.get("isDraft", True):
                    to_field = email.get("to", [])
                    to_emails = []
                    if isinstance(to_field, list):
                        for recipient in to_field:
                            if isinstance(recipient, dict):
                                to_emails.append(recipient.get("email", ""))
                            elif isinstance(recipient, str):
                                to_emails.append(recipient)
                    if target_recipient in to_emails:
                        matching_emails.append(email)

    if not matching_emails:
        return False, (
            f"No sent (non-draft) email found addressed to {target_recipient}. "
            f"Expected a composed and sent email to Sophie Laurent at EuroDesign."
        )

    return True, (
        f"Found {len(matching_emails)} sent email(s) to {target_recipient}. "
        f"Email successfully composed and sent to Sophie Laurent."
    )
