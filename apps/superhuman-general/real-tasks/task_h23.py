import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Check auto label exists
    auto_labels = state.get("autoLabels", [])
    al = None
    for a in auto_labels:
        if a.get("name", "").lower() == "legal notices":
            al = a
            break
    if al is None:
        return False, "No auto label named 'Legal Notices' found."

    criteria = al.get("criteria", {})
    from_field = criteria.get("from", "")
    if "legalwise.com" not in from_field.lower():
        return False, f"Auto label 'Legal Notices' criteria does not match legalwise.com. Got: {criteria}"

    # Check split exists
    splits = state.get("splits", [])
    split = None
    for s in splits:
        if s.get("name", "").lower() == "legal":
            split = s
            break
    if split is None:
        return False, "No split named 'Legal' found."

    split_criteria = split.get("criteria", {})
    auto_label_ref = split_criteria.get("autoLabel", "")
    if auto_label_ref.lower() != "legal notices":
        return False, f"Split 'Legal' does not reference auto label 'Legal Notices'. Got criteria: {split_criteria}"

    return True, "Auto label 'Legal Notices' and split 'Legal' created correctly."
