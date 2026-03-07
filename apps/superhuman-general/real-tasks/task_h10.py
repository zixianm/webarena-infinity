import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])

    # Find all inbox emails from @acmecorp.com
    # Inbox = not isDone, not isTrashed, not isSpam, not isDraft, no remindAt
    acme_inbox_emails = []
    for email in emails:
        from_email = email.get("from", {}).get("email", "")
        if not from_email.endswith("@acmecorp.com"):
            continue
        if email.get("isDone", False):
            continue
        if email.get("isTrashed", False):
            continue
        if email.get("isSpam", False):
            continue
        if email.get("isDraft", False):
            continue
        if email.get("remindAt") is not None:
            continue
        acme_inbox_emails.append(email)

    if not acme_inbox_emails:
        return False, "No Acme Corp teammate emails found in the inbox."

    failures = []
    for email in acme_inbox_emails:
        if not email.get("isStarred", False):
            failures.append(
                f"Email '{email.get('subject')}' (id {email.get('id')}) from "
                f"{email.get('from', {}).get('email', '?')} is in inbox but not starred."
            )

    if failures:
        return False, (
            f"{len(failures)} of {len(acme_inbox_emails)} Acme Corp inbox emails are not starred. "
            + " ".join(failures)
        )

    return True, (
        f"All {len(acme_inbox_emails)} Acme Corp teammate emails in the inbox are starred."
    )
