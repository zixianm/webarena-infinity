import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if "Memory leak in WebSocket" in e["subject"] and e["from"]["email"] == "notifications@github.com"), None)
    if not email:
        return False, "Email about WebSocket memory leak not found."
    if not email["isDone"]:
        return False, "Email should be marked as Done after unsubscribe."
    blocked = state.get("settings", {}).get("blockedSenders", [])
    if "notifications@github.com" not in blocked:
        return False, f"Sender not in blockedSenders. blockedSenders: {blocked}"
    return True, "Unsubscribed from notifications@github.com. Email marked Done and sender blocked."
