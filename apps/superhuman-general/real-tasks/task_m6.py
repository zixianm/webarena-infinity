import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    blocked_senders = settings.get("blockedSenders", [])

    # Check that notifications@github.com is in blocked senders
    github_blocked = False
    for sender in blocked_senders:
        if isinstance(sender, dict):
            if sender.get("email", "") == "notifications@github.com":
                github_blocked = True
                break
        elif isinstance(sender, str):
            if sender == "notifications@github.com":
                github_blocked = True
                break

    if not github_blocked:
        return False, (
            f"'notifications@github.com' is not in blocked senders. "
            f"Current blocked senders: {blocked_senders}"
        )

    # Check that at least one GitHub notification email is marked as done
    emails = state.get("emails", [])
    github_done = False
    for email in emails:
        from_info = email.get("from", {})
        from_email = from_info.get("email", "") if isinstance(from_info, dict) else str(from_info)
        if from_email == "notifications@github.com" and email.get("isDone", False):
            github_done = True
            break

    if not github_done:
        return False, (
            "notifications@github.com is blocked, but no GitHub notification email "
            "is marked as done. Unsubscribing should also archive/mark done existing notifications."
        )

    return True, (
        "Successfully unsubscribed from GitHub notifications: "
        "notifications@github.com is blocked and GitHub emails are marked as done."
    )
