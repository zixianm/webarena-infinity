import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])
    finance_label = None
    for l in state.get("labels", []):
        if l.get("name") == "Finance":
            finance_label = l
            break
    if finance_label is None:
        return False, "Finance label not found."

    finance_id = finance_label["id"]
    priya_emails = [e for e in emails if e.get("from", {}).get("email") == "priya.sharma@acmecorp.com"]

    if not priya_emails:
        return False, "No emails from Priya Sharma found."

    missing = []
    for e in priya_emails:
        if finance_id not in e.get("labels", []):
            missing.append(f"id={e.get('id')} '{e.get('subject','')}'")

    if missing:
        return False, f"{len(missing)} Priya email(s) missing Finance label: {'; '.join(missing)}"

    return True, f"All {len(priya_emails)} emails from Priya Sharma have the Finance label."
