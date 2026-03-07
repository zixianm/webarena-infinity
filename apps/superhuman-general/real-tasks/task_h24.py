import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    snippets = state.get("snippets", [])
    user_id = state.get("currentUser", {}).get("id", "user_1")

    user_snippets = [s for s in snippets if s.get("authorId") == user_id]
    if not user_snippets:
        return False, "No snippets found authored by the current user."

    not_shared = [s for s in user_snippets if not s.get("isShared", False)]
    if not_shared:
        names = [s.get("name", "?") for s in not_shared]
        return False, f"{len(not_shared)} personal snippet(s) not shared: {', '.join(names)}"

    return True, f"All {len(user_snippets)} personal snippets are shared with the team."
