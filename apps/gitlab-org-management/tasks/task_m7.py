import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify Platform Engineering description and requireTwoFactor were updated."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Platform Engineering is group ID 1
    pe_group = next((g for g in state["groups"] if g["id"] == 1), None)
    if not pe_group:
        return False, "Platform Engineering group (id=1) not found."

    expected_desc = "Core infrastructure and platform services"
    if pe_group.get("description") != expected_desc:
        return False, f"Expected description '{expected_desc}', got '{pe_group.get('description')}'."

    if pe_group.get("requireTwoFactor") is not True:
        return False, f"Expected requireTwoFactor=true, got '{pe_group.get('requireTwoFactor')}'."

    return True, "Platform Engineering description and requireTwoFactor updated correctly."
