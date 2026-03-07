import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    labels = state.get("labels", [])
    vip_label = None
    for l in labels:
        if l.get("name", "").lower() == "vip":
            vip_label = l
            break
    if vip_label is None:
        return False, "No label named 'VIP' found."

    color = (vip_label.get("color") or "").lower()
    red_colors = ["#f44336", "#ff0000", "#e53935", "#d32f2f", "#c62828", "#b71c1c", "#ff1744", "#ff5252", "#ef5350", "red"]
    if not any(r in color for r in red_colors):
        return False, f"Label 'VIP' color '{color}' does not appear to be red."

    vip_id = vip_label["id"]
    emails = state.get("emails", [])
    starred = [e for e in emails if e.get("isStarred", False)]
    if not starred:
        return False, "No starred emails found in state."

    missing = []
    for e in starred:
        if vip_id not in e.get("labels", []):
            missing.append(f"Email id={e.get('id')} '{e.get('subject', '')}'")
    if missing:
        return False, f"VIP label missing from {len(missing)} starred email(s): {'; '.join(missing[:3])}"

    return True, f"Label 'VIP' (red) exists and applied to all {len(starred)} starred emails."
