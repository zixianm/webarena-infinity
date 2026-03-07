import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    snippets = state.get("snippets", [])
    if not snippets:
        return False, "No snippets found in state."

    match = None
    for snippet in snippets:
        name = snippet.get("name", "")
        if name.strip().lower() == "nda request":
            match = snippet
            break

    if not match:
        names = [s.get("name", "") for s in snippets]
        return False, f"No snippet named 'NDA Request' found. Existing snippets: {names}"

    if not match.get("isShared", False):
        return False, f"Snippet 'NDA Request' exists but isShared is {match.get('isShared')}, expected True."

    body = match.get("body", "")
    if not body or not body.strip():
        return False, "Snippet 'NDA Request' exists but has an empty body."

    return True, (
        f"Snippet 'NDA Request' created successfully: isShared=True, "
        f"body length={len(body)} characters."
    )
