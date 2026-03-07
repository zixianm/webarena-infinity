import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    blocked = settings.get("blockedSenders", [])

    newsletter_senders = [
        "newsletter@theinformation.com",
        "newsletter@techcrunch.com",
        "hello@producthunt.com",
        "crew@morningbrew.com",
        "digest@hackernewsletter.com",
    ]

    missing = [s for s in newsletter_senders if s not in blocked]
    if missing:
        return False, f"{len(missing)} newsletter sender(s) not unsubscribed: {', '.join(missing)}"

    return True, f"All {len(newsletter_senders)} newsletter senders have been unsubscribed (blocked)."
