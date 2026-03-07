import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])
    target = "michael.f@cloudscale.dev"
    user_email = state.get("currentUser", {}).get("email", "alex.morgan@acmecorp.com")

    for e in emails:
        if e.get("isDraft", False):
            continue
        from_email = e.get("from", {}).get("email", "")
        if from_email != user_email:
            continue
        to_list = e.get("to", [])
        for t in to_list:
            addr = t.get("email", "") if isinstance(t, dict) else t
            if addr == target:
                return True, f"Found sent email to {target} (id={e.get('id')})."

    return False, f"No sent (non-draft) email found addressed to {target}."
