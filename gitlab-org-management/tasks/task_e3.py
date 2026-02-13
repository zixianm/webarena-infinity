import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the current user's bio has been changed."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    expected_bio = "Full-stack developer with 10 years of experience"

    # Check currentUser bio
    current_user = state.get("currentUser", {})
    if current_user.get("bio") != expected_bio:
        return False, f"Expected bio '{expected_bio}', got '{current_user.get('bio')}'."

    # Also verify the users array is synced
    user_in_array = next(
        (u for u in state["users"] if u["id"] == current_user["id"]), None
    )
    if user_in_array and user_in_array.get("bio") != expected_bio:
        return False, "Bio updated in currentUser but not synced to users array."

    return True, "Bio successfully updated to expected value."
