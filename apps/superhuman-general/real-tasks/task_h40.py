import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    failures = []

    ar = settings.get("autoReminders", {})
    if ar.get("mode") != "external":
        failures.append(f"Auto-reminders mode is '{ar.get('mode')}', expected 'external'.")

    ad = settings.get("autoDrafts", {})
    if ad.get("enabled") is not False:
        failures.append(f"Auto drafts still enabled (enabled={ad.get('enabled')}).")

    auto_labels = state.get("autoLabels", [])
    shipping = None
    for al in auto_labels:
        if al.get("name") == "Shipping Update":
            shipping = al
            break
    if shipping is None:
        failures.append("Shipping Update auto label not found.")
    elif not shipping.get("enabled", False):
        failures.append(f"Shipping Update auto label is disabled (enabled={shipping.get('enabled')}).")

    if failures:
        return False, "; ".join(failures)

    return True, "Auto-reminders set to external, auto drafts disabled, Shipping Update enabled."
