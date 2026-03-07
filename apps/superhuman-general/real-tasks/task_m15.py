import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])

    target_subject = "Re: Series B Term Sheet Discussion"
    target_from = "emily.r@venturelabs.co"

    for email in emails:
        subject = email.get("subject", "")
        sender = email.get("from", {})
        sender_email = sender.get("email", "") if isinstance(sender, dict) else sender

        if subject == target_subject and sender_email == target_from:
            is_done = email.get("isDone", False)
            is_read = email.get("isRead", True)
            is_trashed = email.get("isTrashed", False)
            is_spam = email.get("isSpam", False)
            remind_at = email.get("remindAt")

            errors = []
            if is_done:
                errors.append(f"isDone is {is_done}, expected False")
            if is_read:
                errors.append(f"isRead is {is_read}, expected False")
            if is_trashed:
                errors.append(f"isTrashed is {is_trashed}, expected False")
            if is_spam:
                errors.append(f"isSpam is {is_spam}, expected False")
            if remind_at is not None:
                errors.append(f"remindAt is '{remind_at}', expected None/null")

            if errors:
                return False, (
                    f"Found email '{target_subject}' from {target_from}, "
                    f"but conditions not met: {'; '.join(errors)}."
                )

            return True, (
                f"Email '{target_subject}' from {target_from} is correctly "
                "in inbox (isDone=False, isTrashed=False, isSpam=False, remindAt=null) "
                "and marked unread (isRead=False)."
            )

    return False, f"Could not find email with subject '{target_subject}' from '{target_from}'."
