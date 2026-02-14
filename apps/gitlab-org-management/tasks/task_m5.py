import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Maria Rodriguez was removed from the Product Development group."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Maria Rodriguez is user ID 4, Product Development is group ID 2
    maria_id = 4
    pd_group_id = 2

    # Check that no direct membership exists
    direct_membership = next(
        (
            m
            for m in state["groupMemberships"]
            if m["groupId"] == pd_group_id
            and m["userId"] == maria_id
            and m.get("membershipType") == "direct"
        ),
        None,
    )
    if direct_membership:
        return False, "Maria Rodriguez still has a direct membership in Product Development."

    return True, "Maria Rodriguez successfully removed from Product Development."
