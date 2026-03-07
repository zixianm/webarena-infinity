import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    snippets = state.get("snippets", [])

    # These snippets had open rates below 80% and should be deleted
    should_be_deleted = {
        "[Sales] Product Demo": 0.76,
        "[Engineering] Bug Report Response": 0.71,
        "[Marketing] Event Invitation": 0.68,
    }

    still_exists = []
    for s in snippets:
        name = s.get("name", "")
        if name in should_be_deleted:
            still_exists.append(f"'{name}' (open rate {should_be_deleted[name]})")

    if still_exists:
        return False, f"Snippets with <80% open rate still exist: {', '.join(still_exists)}"

    # Make sure we didn't delete snippets that should remain
    if len(snippets) < 9:
        return False, f"Too many snippets deleted. Expected 9 remaining, found {len(snippets)}."

    return True, "All snippets with open rate below 80% have been deleted."
