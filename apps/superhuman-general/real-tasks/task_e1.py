import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    theme = settings.get("theme")
    if theme == "dark":
        return True, "Theme is set to dark mode."
    return False, f"Expected theme to be 'dark', but got '{theme}'."
