import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    split = next((s for s in state["splits"] if s["name"] == "Investors"), None)
    if not split:
        return False, "Split 'Investors' not found."
    criteria = split.get("criteria", {})
    if criteria.get("autoLabel") != "Investor":
        return False, f"Split criteria should be autoLabel 'Investor', got {criteria}."
    return True, "Split 'Investors' created with correct criteria."
