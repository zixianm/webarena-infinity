import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    splits = state.get("splits", [])
    for split in splits:
        if split.get("name") == "Feeds":
            return False, "The 'Feeds' split still exists in the inbox."
    return True, "The 'Feeds' split has been successfully removed from the inbox."
