import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    labels = state.get("labels", [])

    # Find a label named "Partnerships"
    partnerships_label = None
    for label in labels:
        if label.get("name") == "Partnerships":
            partnerships_label = label
            break

    if partnerships_label is None:
        # Check case-insensitive as a fallback
        for label in labels:
            if label.get("name", "").lower() == "partnerships":
                partnerships_label = label
                break

    if partnerships_label is None:
        label_names = [l.get("name") for l in labels]
        return False, (
            f"No label named 'Partnerships' found. Existing labels: {label_names}"
        )

    # Check that it's a user-created label
    label_type = partnerships_label.get("type", "")
    if label_type != "user":
        return False, (
            f"Label 'Partnerships' exists but has type '{label_type}' instead of 'user'."
        )

    # Check that it has a color set
    color = partnerships_label.get("color")
    if not color:
        return False, "Label 'Partnerships' exists but has no color set."

    return True, (
        f"Label 'Partnerships' exists with type 'user' and color '{color}'."
    )
