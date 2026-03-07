import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    snippets = state.get("snippets", [])

    # Find the "Scheduling Request" snippet
    target_snippet = None
    for snippet in snippets:
        if snippet.get("name") == "Scheduling Request":
            target_snippet = snippet
            break

    if target_snippet is None:
        # Try case-insensitive match
        for snippet in snippets:
            if snippet.get("name", "").lower() == "scheduling request":
                target_snippet = snippet
                break

    if target_snippet is None:
        snippet_names = [s.get("name") for s in snippets]
        return False, (
            f"Could not find snippet named 'Scheduling Request'. "
            f"Existing snippets: {snippet_names}"
        )

    is_shared = target_snippet.get("isShared")
    if is_shared is not True:
        return False, (
            f"Snippet 'Scheduling Request' found but isShared is {is_shared}, expected True."
        )

    return True, "Snippet 'Scheduling Request' is now shared with the team (isShared=True)."
