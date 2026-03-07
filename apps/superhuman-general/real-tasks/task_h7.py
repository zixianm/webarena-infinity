import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])
    engineering_label = "label_11"

    engineering_emails = [
        email for email in emails
        if engineering_label in email.get("labels", [])
    ]

    if not engineering_emails:
        return False, "No emails with the 'Engineering' label (label_11) found in state."

    failures = []
    for email in engineering_emails:
        if not email.get("isDone", False):
            failures.append(
                f"Email '{email.get('subject')}' (id {email.get('id')}) has 'Engineering' label "
                f"but isDone={email.get('isDone')} (expected True)."
            )

    if failures:
        return False, (
            f"{len(failures)} of {len(engineering_emails)} Engineering-labeled emails "
            f"are not marked as done. " + " ".join(failures)
        )

    return True, (
        f"All {len(engineering_emails)} emails with the 'Engineering' label are marked as done."
    )
