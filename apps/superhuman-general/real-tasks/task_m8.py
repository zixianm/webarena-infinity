import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    auto_reminders = settings.get("autoReminders", {})
    mode = auto_reminders.get("mode")

    if mode is None:
        return False, (
            "Could not find settings.autoReminders.mode in state. "
            f"Auto-reminders settings: {auto_reminders}"
        )

    if mode != "external":
        return False, (
            f"Auto-reminder mode is set to '{mode}', expected 'external'."
        )

    return True, "Auto-reminder mode correctly set to 'external' (only external emails)."
