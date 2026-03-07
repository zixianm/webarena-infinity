import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])

    # Find a sent (non-draft) email to emily.r@venturelabs.co
    matching_emails = []
    for email in emails:
        # Check if this email is from the user
        from_info = email.get("from", {})
        from_email = from_info.get("email", "") if isinstance(from_info, dict) else str(from_info)
        if from_email != "alex.morgan@acmecorp.com":
            continue

        # Check recipients - could be in "to" field as array of objects or strings
        to_field = email.get("to", [])
        recipient_match = False
        if isinstance(to_field, list):
            for recipient in to_field:
                if isinstance(recipient, dict):
                    if recipient.get("email", "") == "emily.r@venturelabs.co":
                        recipient_match = True
                        break
                elif isinstance(recipient, str):
                    if "emily.r@venturelabs.co" in recipient:
                        recipient_match = True
                        break
        elif isinstance(to_field, str):
            if "emily.r@venturelabs.co" in to_field:
                recipient_match = True

        if recipient_match:
            matching_emails.append(email)

    if not matching_emails:
        return False, (
            "No email found from alex.morgan@acmecorp.com to emily.r@venturelabs.co."
        )

    # Check that at least one matching email is not a draft
    sent_emails = [e for e in matching_emails if e.get("isDraft") is not True]

    if not sent_emails:
        return False, (
            "Found email(s) to emily.r@venturelabs.co but they are all drafts (isDraft=True). "
            "The email should be sent, not saved as a draft."
        )

    # Verify the sent email has some content
    sent_email = sent_emails[0]
    subject = sent_email.get("subject", "")
    body = sent_email.get("body", "")

    if not subject and not body:
        return False, (
            "Found a sent email to emily.r@venturelabs.co but it has no subject or body content."
        )

    return True, (
        f"Email sent to emily.r@venturelabs.co with subject '{subject}' (isDraft=False)."
    )
