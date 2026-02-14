import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that 'alex.personal@email.com' has been removed from secondary emails."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    target_email = "alex.personal@email.com"

    current_user = state.get("currentUser", {})
    secondary_emails = current_user.get("secondaryEmails", [])

    if target_email in secondary_emails:
        return False, f"Email '{target_email}' still present in secondary emails."

    return True, f"Email '{target_email}' successfully removed from secondary emails."
