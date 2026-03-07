import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    signature = settings.get("signature", "")

    if not signature:
        return False, "No email signature found in state['settings']['signature']."

    failures = []

    if "Chief Product Officer" not in signature:
        failures.append(
            "Signature does not contain 'Chief Product Officer'."
        )

    if "VP of Product" in signature:
        failures.append(
            "Signature still contains 'VP of Product' (should have been replaced)."
        )

    if failures:
        return False, " ".join(failures) + f" Current signature: '{signature}'."

    return True, "Email signature updated to use 'Chief Product Officer' instead of 'VP of Product'."
