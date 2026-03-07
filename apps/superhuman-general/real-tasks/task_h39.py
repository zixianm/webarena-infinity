import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    events = state.get("calendarEvents", [])
    failures = []

    personal_events = [e for e in events if e.get("calendarId") == "personal"]
    if personal_events:
        names = [e.get("title", "?") for e in personal_events]
        failures.append(f"{len(personal_events)} personal event(s) still exist: {', '.join(names)}")

    settings = state.get("settings", {})
    stz = settings.get("secondaryTimezone", "")
    if stz and stz.strip():
        failures.append(f"Secondary timezone still set to '{stz}', should be empty.")

    if failures:
        return False, "; ".join(failures)

    work_events = [e for e in events if e.get("calendarId") == "work"]
    return True, f"All personal calendar events deleted and secondary timezone removed. {len(work_events)} work events remain."
