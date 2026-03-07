import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    notifications = settings.get("notifications", {})
    alert_minutes = notifications.get("alertMinutes")

    if alert_minutes is None:
        return False, (
            "Could not find settings.notifications.alertMinutes in state. "
            f"Notifications settings: {notifications}"
        )

    # Accept both int and string "30"
    try:
        alert_value = int(alert_minutes)
    except (ValueError, TypeError):
        return False, (
            f"settings.notifications.alertMinutes has unexpected value: {alert_minutes}"
        )

    if alert_value != 30:
        return False, (
            f"Calendar alert timing is set to {alert_value} minutes, expected 30 minutes."
        )

    return True, "Calendar alert timing correctly set to 30 minutes before events."
