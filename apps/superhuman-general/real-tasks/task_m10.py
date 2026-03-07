import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    labels = state.get("labels", [])

    # Check that no label with name "Receipts" exists
    for label in labels:
        if label.get("name") == "Receipts":
            return False, (
                f"Label 'Receipts' still exists (id: {label.get('id')}). "
                "It should have been deleted."
            )

    # Check that no email still references label_13 (the Receipts label ID)
    emails = state.get("emails", [])
    emails_with_old_label = []
    for email in emails:
        email_labels = email.get("labels", [])
        if "label_13" in email_labels:
            emails_with_old_label.append(email.get("subject", email.get("id", "unknown")))

    if emails_with_old_label:
        return False, (
            f"Label 'Receipts' was removed from labels list, but {len(emails_with_old_label)} "
            f"email(s) still reference 'label_13': {emails_with_old_label}. "
            "Deleting a label should also clean up references in emails."
        )

    return True, (
        "Label 'Receipts' successfully deleted and no emails reference 'label_13' anymore."
    )
