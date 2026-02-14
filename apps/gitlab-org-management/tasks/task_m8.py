import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Security's group share to Platform Engineering was revoked."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # The share is: Security (group 4) shared INTO Platform Engineering (group 1)
    # sourceGroupId=4, targetGroupId=1
    share = next(
        (
            s
            for s in state["groupShares"]
            if s["sourceGroupId"] == 4 and s["targetGroupId"] == 1
        ),
        None,
    )
    if share:
        return False, "Group share from Security to Platform Engineering still exists."

    return True, "Security's access to Platform Engineering has been successfully revoked."
