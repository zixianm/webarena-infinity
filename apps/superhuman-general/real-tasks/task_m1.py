import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the email from David Kim about FinancePlus partnership
    emails = state.get("emails", [])
    target_email = None
    for email in emails:
        if (email.get("subject") == "Partnership Opportunity - FinancePlus x Acme"
                and email.get("from", {}).get("email", "") == "david.kim@financeplus.com"):
            target_email = email
            break

    if target_email is None:
        # Try matching by sender email alone if subject differs slightly
        for email in emails:
            if email.get("from", {}).get("email", "") == "david.kim@financeplus.com":
                target_email = email
                break

    if target_email is None:
        return False, "Could not find the FinancePlus partnership email from David Kim."

    email_labels = target_email.get("labels", [])

    # Check for Finance label (label_3)
    has_finance = "label_3" in email_labels
    # Check for Clients label (label_4)
    has_clients = "label_4" in email_labels

    if not has_finance and not has_clients:
        return False, (
            f"Email is missing both 'Finance' (label_3) and 'Clients' (label_4) labels. "
            f"Current labels: {email_labels}"
        )
    if not has_finance:
        return False, (
            f"Email is missing 'Finance' (label_3) label. Current labels: {email_labels}"
        )
    if not has_clients:
        return False, (
            f"Email is missing 'Clients' (label_4) label. Current labels: {email_labels}"
        )

    return True, "Email from David Kim correctly labeled with both 'Finance' and 'Clients'."
