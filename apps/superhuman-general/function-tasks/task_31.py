import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    al = next((a for a in state["autoLabels"] if a["name"] == "Engineering Alerts"), None)
    if not al:
        return False, "Auto label 'Engineering Alerts' not found."
    if al.get("type") != "custom":
        return False, f"Auto label type should be 'custom', got '{al.get('type')}'."
    criteria = al.get("criteria", {})
    from_val = criteria.get("from", "")
    if "@sentry.io" not in from_val:
        return False, f"Auto label from criteria should contain '@sentry.io', got '{from_val}'."
    return True, "Auto label 'Engineering Alerts' created with correct criteria."
