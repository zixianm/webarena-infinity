import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    swipe_right = settings.get("swipeRight")
    swipe_left = settings.get("swipeLeft")

    errors = []
    if swipe_right != "star":
        errors.append(f"swipeRight is '{swipe_right}', expected 'star'")
    if swipe_left != "spam":
        errors.append(f"swipeLeft is '{swipe_left}', expected 'spam'")

    if errors:
        return False, f"Swipe action settings incorrect: {'; '.join(errors)}."

    return True, "Swipe right is correctly set to 'star' and swipe left is correctly set to 'spam'."
