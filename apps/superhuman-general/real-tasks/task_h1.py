import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])
    failures = []
    found_any = False

    for email in emails:
        # Match unread newsletters in the Other split that were in the inbox
        if (
            email.get("splitCategory") == "other"
            and email.get("autoLabel") == "Newsletter"
            and not email.get("isTrashed", False)
            and not email.get("isSpam", False)
            and not email.get("isDraft", False)
        ):
            # Email 29 is the only one that was originally unread and in inbox
            # (not isDone, no remindAt). We check by subject since that's the
            # definitive marker for the originally-unread newsletter.
            if "AI Startup Funding" in email.get("subject", ""):
                found_any = True
                if not email.get("isDone", False):
                    failures.append(
                        f"Email '{email.get('subject')}' (id {email.get('id')}) "
                        f"should be archived (isDone=True) but isDone={email.get('isDone')}."
                    )

    if not found_any:
        return False, "Could not find the unread newsletter email about 'AI Startup Funding'."

    if failures:
        return False, " ".join(failures)

    return True, "All unread newsletter emails from the Other split have been archived."
