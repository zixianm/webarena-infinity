import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    snippets = state.get("snippets", [])

    # Find a snippet named "Investor Update"
    target_snippet = None
    for snippet in snippets:
        if snippet.get("name") == "Investor Update":
            target_snippet = snippet
            break

    if target_snippet is None:
        # Try case-insensitive match
        for snippet in snippets:
            if snippet.get("name", "").lower() == "investor update":
                target_snippet = snippet
                break

    if target_snippet is None:
        snippet_names = [s.get("name") for s in snippets]
        return False, (
            f"No snippet named 'Investor Update' found. "
            f"Existing snippets: {snippet_names}"
        )

    # Check that the snippet has a body (non-empty)
    body = target_snippet.get("body", "")
    if not body:
        return False, (
            "Snippet 'Investor Update' exists but has an empty body."
        )

    return True, (
        f"Snippet 'Investor Update' created successfully with body content."
    )
