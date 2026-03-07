import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    if not settings:
        return False, "No settings found in state."

    failures = []

    # Check theme is "auto" (System maps to "auto")
    theme = settings.get("theme", "")
    if theme != "auto":
        failures.append(f"theme is '{theme}', expected 'auto' (System)")

    # Check sound notifications disabled
    notifications = settings.get("notifications", {})
    sound = notifications.get("sound")
    if sound is not False:
        failures.append(f"notifications.sound is {sound}, expected False")

    # Check calendar alert timing is 5 minutes
    alert_minutes = notifications.get("alertMinutes")
    if alert_minutes != 5:
        failures.append(f"notifications.alertMinutes is {alert_minutes}, expected 5")

    if failures:
        return False, "Settings not correctly configured: " + "; ".join(failures)

    return True, "Settings updated: theme=auto (System), sound notifications disabled, calendar alerts set to 5 minutes."
