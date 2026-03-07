import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    auto_labels = state.get("autoLabels", [])

    for label in auto_labels:
        name = label.get("name", "")
        if name == "Design Review":
            label_type = label.get("type", "")
            enabled = label.get("enabled", False)
            criteria = label.get("criteria", {})

            errors = []
            if label_type != "custom":
                errors.append(f"type is '{label_type}', expected 'custom'")
            if enabled is not True:
                errors.append(f"enabled is {enabled}, expected True")

            # Check criteria for designhub.io in from field
            from_field = criteria.get("from", "")
            if isinstance(from_field, list):
                from_str = " ".join(str(f) for f in from_field).lower()
            else:
                from_str = str(from_field).lower()

            if "designhub.io" not in from_str:
                errors.append(
                    f"criteria.from does not contain 'designhub.io', found '{from_field}'"
                )

            if errors:
                return False, (
                    f"Found auto label 'Design Review', but conditions not met: "
                    f"{'; '.join(errors)}."
                )

            return True, (
                "Auto label 'Design Review' exists with type 'custom', enabled=True, "
                "and criteria matching emails from designhub.io."
            )

    return False, (
        f"No auto label named 'Design Review' found. "
        f"Found {len(auto_labels)} auto label(s): "
        f"{[l.get('name') for l in auto_labels]}."
    )
