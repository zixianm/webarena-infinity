import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])
    target_subject = "Patent Filing Deadline - April 15"
    target_from = "james.obrien@legalwise.com"

    patent_email = None
    for email in emails:
        subject = email.get("subject", "")
        from_email = email.get("from", {}).get("email", "")
        if target_subject in subject and from_email == target_from:
            patent_email = email
            break

    if patent_email is None:
        return False, (
            f"Could not find email with subject containing '{target_subject}' "
            f"from '{target_from}'."
        )

    failures = []

    # Check reminder is cleared
    remind_at = patent_email.get("remindAt")
    if remind_at is not None:
        failures.append(
            f"Reminder should be cleared (remindAt=None) but remindAt='{remind_at}'."
        )

    # Check Urgent label is present
    labels = patent_email.get("labels", [])
    if "label_5" not in labels:
        failures.append(
            f"Email should have the 'Urgent' label (label_5) but current labels are: {labels}."
        )

    if failures:
        return False, f"Email '{target_subject}': " + " ".join(failures)

    return True, (
        f"Patent filing email from James O'Brien has reminder cleared and 'Urgent' label added."
    )
