import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Check that no label named "Marketing" exists
    labels = state.get("labels", [])
    for label in labels:
        label_name = label.get("name", "")
        if label_name.lower() == "marketing":
            return False, f"Label 'Marketing' still exists in labels (id={label.get('id')})."

    # Check that no email has label_12 in its labels array
    emails = state.get("emails", [])
    emails_with_marketing = []
    for email in emails:
        email_labels = email.get("labels", [])
        if "label_12" in email_labels:
            emails_with_marketing.append(email.get("id"))

    if emails_with_marketing:
        return False, (
            f"Label 'Marketing' (label_12) still found on {len(emails_with_marketing)} emails: "
            f"{emails_with_marketing}"
        )

    return True, "Label 'Marketing' has been deleted and removed from all emails."
