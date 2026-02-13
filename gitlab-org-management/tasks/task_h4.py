import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify username changed to 'alex.m' and display name changed to 'Alex M.'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    current_user = state.get("currentUser", {})

    # Check username
    if current_user.get("username") != "alex.m":
        return False, f"Expected username 'alex.m', got '{current_user.get('username')}'."

    # Check display name
    if current_user.get("name") != "Alex M.":
        return False, f"Expected name 'Alex M.', got '{current_user.get('name')}'."

    # Verify sync with users array
    user_in_array = next(
        (u for u in state["users"] if u["id"] == current_user["id"]), None
    )
    if user_in_array:
        if user_in_array.get("username") != "alex.m":
            return False, "Username updated in currentUser but not synced to users array."
        if user_in_array.get("name") != "Alex M.":
            return False, "Name updated in currentUser but not synced to users array."

    return True, "Username changed to 'alex.m' and display name changed to 'Alex M.'."
