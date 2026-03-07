import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    if not settings:
        return False, "No settings found in state."

    checks = {
        "instantReply": settings.get("instantReply", {}).get("enabled"),
        "smartSend": settings.get("smartSend", {}).get("enabled"),
        "askAi": settings.get("askAi", {}).get("enabled"),
        "autoReminders": settings.get("autoReminders", {}).get("enabled"),
    }

    failures = []
    for feature, value in checks.items():
        if value is None:
            failures.append(f"{feature}.enabled not found in settings")
        elif value is not False:
            failures.append(f"{feature}.enabled is {value}, expected False")

    if failures:
        return False, "AI features not all disabled: " + "; ".join(failures)

    return True, "All AI features disabled: Instant Reply, Smart Send, Ask AI, and Auto Reminders."
