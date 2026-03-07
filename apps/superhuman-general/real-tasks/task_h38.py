import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    labels = state.get("labels", [])
    ar_label = None
    for l in labels:
        name = l.get("name", "").lower()
        if "awaiting" in name and "reply" in name:
            ar_label = l
            break
    if ar_label is None:
        return False, "No label matching 'Awaiting Reply' found."

    color = (ar_label.get("color") or "").lower()
    yellow_colors = ["#ffeb3b", "#ffc107", "#ff9800", "#fdd835", "#fbc02d", "#f9a825", "#ffee58", "#fff176", "#ffca28", "yellow", "#ffff00"]
    if not any(y in color for y in yellow_colors):
        return False, f"Label 'Awaiting Reply' color '{color}' does not appear to be yellow."

    ar_id = ar_label["id"]
    user_email = state.get("currentUser", {}).get("email", "alex.morgan@acmecorp.com")

    # Find sent emails with reminders
    sent_reminded_ids = {111, 112}
    email_map = {e.get("id"): e for e in state.get("emails", [])}

    failures = []
    for eid in sent_reminded_ids:
        e = email_map.get(eid)
        if e is None:
            failures.append(f"Email id={eid} not found")
            continue
        if ar_id not in e.get("labels", []):
            failures.append(f"Email id={eid} '{e.get('subject','')}' missing Awaiting Reply label")

    if failures:
        return False, "; ".join(failures)

    return True, f"Label 'Awaiting Reply' (yellow) created and applied to {len(sent_reminded_ids)} sent reminder emails."
