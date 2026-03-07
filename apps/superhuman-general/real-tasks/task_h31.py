import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])
    email_map = {e.get("id"): e for e in emails}

    # Email 4: the threaded migration email
    threaded = email_map.get(4)
    if threaded is None:
        return False, "Email id=4 (Infrastructure Migration Plan) not found."

    if not threaded.get("isStarred", False):
        return False, "Email 'Re: Infrastructure Migration Plan' (id=4, with thread) is not starred."

    # Email 127: the standalone sign-off — should NOT be starred
    signoff = email_map.get(127)
    if signoff and signoff.get("isStarred", False):
        return False, "Email 'Infrastructure Migration Sign-off' (id=127) was incorrectly starred. Only the threaded one should be starred."

    return True, "Correct email (id=4, with thread) is starred; sign-off (id=127) is not."
