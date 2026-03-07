import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    snippet = next((s for s in state["snippets"] if s["name"] == "Project Update"), None)
    if not snippet:
        return False, "Snippet 'Project Update' not found."
    body = snippet.get("body", "")
    if "{first_name}" not in body:
        return False, "Snippet body missing {first_name} variable."
    if "{project_name}" not in body:
        return False, "Snippet body missing {project_name} variable."
    return True, "Snippet 'Project Update' created with correct body and variables."
