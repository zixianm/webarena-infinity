import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])

    # Find the budget approval email from Priya
    target_email = None
    for email in emails:
        subject = email.get("subject", "")
        from_info = email.get("from", {})
        from_email = from_info.get("email", "") if isinstance(from_info, dict) else str(from_info)

        if ("Budget Approval" in subject
                and from_email == "priya.sharma@acmecorp.com"):
            target_email = email
            break

    if target_email is None:
        # Broader search by sender
        for email in emails:
            from_info = email.get("from", {})
            from_email = from_info.get("email", "") if isinstance(from_info, dict) else str(from_info)
            if from_email == "priya.sharma@acmecorp.com":
                target_email = email
                break

    if target_email is None:
        return False, (
            "Could not find the budget approval email from priya.sharma@acmecorp.com."
        )

    remind_at = target_email.get("remindAt")
    if remind_at is None:
        return False, (
            f"Found the budget approval email from Priya (subject: '{target_email.get('subject')}') "
            f"but remindAt is not set (None). Expected a reminder to be set for next week."
        )

    return True, (
        f"Reminder set on budget approval email from Priya. remindAt = '{remind_at}'."
    )
