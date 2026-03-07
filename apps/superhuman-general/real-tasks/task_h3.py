import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    splits = state.get("splits", [])
    if not isinstance(splits, list):
        return False, f"Expected 'splits' to be a list, got {type(splits).__name__}."

    investor_split = None
    for split in splits:
        name = split.get("name", "")
        if name.lower() == "investors":
            investor_split = split
            break

    if investor_split is None:
        return False, "No split named 'Investors' found in state['splits']."

    # Check that the split's criteria references the Investor autoLabel
    criteria = investor_split.get("criteria", {})
    # The criteria might be stored in different ways depending on the app implementation.
    # Check common patterns: criteria.autoLabel, criteria.filter.autoLabel, or criteria as a string.
    auto_label = criteria.get("autoLabel") if isinstance(criteria, dict) else None

    if auto_label == "Investor":
        return True, "Split 'Investors' exists with correct autoLabel criteria ('Investor')."

    # Also check nested structures
    if isinstance(criteria, dict):
        filter_obj = criteria.get("filter", {})
        if isinstance(filter_obj, dict) and filter_obj.get("autoLabel") == "Investor":
            return True, "Split 'Investors' exists with correct autoLabel criteria ('Investor')."

    # Check if autoLabel is anywhere in the split definition itself
    if investor_split.get("autoLabel") == "Investor":
        return True, "Split 'Investors' exists with correct autoLabel criteria ('Investor')."

    return False, (
        f"Split 'Investors' exists but its criteria does not match autoLabel 'Investor'. "
        f"Split data: {investor_split}."
    )
