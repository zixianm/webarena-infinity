import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Yuki Tanaka was added as Developer to the CI/CD group."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Yuki Tanaka is user ID 8, CI/CD group is ID 7
    yuki_id = 8
    cicd_group_id = 7

    # Verify the user and group exist
    yuki = next((u for u in state["users"] if u["id"] == yuki_id), None)
    if not yuki:
        return False, "User Yuki Tanaka (id=8) not found."

    cicd = next((g for g in state["groups"] if g["id"] == cicd_group_id), None)
    if not cicd:
        return False, "CI/CD group (id=7) not found."

    # Check for direct membership
    membership = next(
        (
            m
            for m in state["groupMemberships"]
            if m["groupId"] == cicd_group_id
            and m["userId"] == yuki_id
            and m.get("membershipType") == "direct"
        ),
        None,
    )
    if not membership:
        return False, "Yuki Tanaka does not have a direct membership in the CI/CD group."

    if membership.get("role") != "Developer":
        return False, f"Expected role 'Developer', got '{membership.get('role')}'."

    return True, "Yuki Tanaka added as Developer to CI/CD group."
