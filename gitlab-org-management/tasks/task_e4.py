import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that 'alex.backup@gmail.com' was added as a secondary email."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    target_email = "alex.backup@gmail.com"

    current_user = state.get("currentUser", {})
    secondary_emails = current_user.get("secondaryEmails", [])

    if target_email not in secondary_emails:
        return False, f"Email '{target_email}' not found in secondary emails. Current: {secondary_emails}"

    return True, f"Email '{target_email}' successfully added as secondary email."
