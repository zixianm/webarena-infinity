import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])
    if not emails:
        return False, "No emails found in state."

    spam_senders = {
        "prince.okafor@yahoo.ng",
        "invest@cryptogainsnow.biz",
        "deals@pharma-discount.xyz",
    }
    spam_ids = {75, 76, 77}

    failures = []
    found_any = False

    for email in emails:
        email_id = email.get("id")
        from_field = email.get("from", {})
        sender = from_field.get("email", "") if isinstance(from_field, dict) else from_field
        is_spam = email.get("isSpam", False)

        if email_id in spam_ids or sender in spam_senders or is_spam:
            found_any = True
            if not email.get("isTrashed", False):
                return False, (
                    f"Email id={email_id} from '{sender}' (spam) is not trashed. "
                    f"isTrashed={email.get('isTrashed')}"
                )

    if not found_any:
        return False, "No spam emails found by id or sender. They may have been deleted entirely."

    return True, "All spam emails (ids 75, 76, 77) are now trashed."
