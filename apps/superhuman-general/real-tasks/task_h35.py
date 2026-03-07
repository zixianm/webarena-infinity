import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    failures = []

    theme = settings.get("theme", "")
    if theme != "dark":
        failures.append(f"Theme is '{theme}', expected 'dark'.")

    tz = settings.get("timezone", "")
    if "los_angeles" not in tz.lower() and "pacific" not in tz.lower():
        failures.append(f"Primary timezone is '{tz}', expected Pacific Time (America/Los_Angeles).")

    stz = settings.get("secondaryTimezone", "")
    if "tokyo" not in stz.lower():
        failures.append(f"Secondary timezone is '{stz}', expected Tokyo (Asia/Tokyo).")

    if failures:
        return False, "; ".join(failures)

    return True, "Theme set to dark, primary TZ to Pacific, secondary TZ to Tokyo."
