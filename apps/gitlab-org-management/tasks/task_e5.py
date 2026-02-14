import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that two-factor authentication has been turned off."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    current_user = state.get("currentUser", {})
    if current_user.get("twoFactorEnabled") is not False:
        return False, f"Expected twoFactorEnabled=false, got '{current_user.get('twoFactorEnabled')}'."

    # Verify sync with users array
    user_in_array = next(
        (u for u in state["users"] if u["id"] == current_user["id"]), None
    )
    if user_in_array and user_in_array.get("twoFactorEnabled") is not False:
        return False, "2FA disabled in currentUser but not synced to users array."

    return True, "Two-factor authentication successfully disabled."
