import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    auto_archive_enabled = state.get("settings", {}).get("autoArchive", {}).get("enabled")
    if auto_archive_enabled is False:
        return True, "Auto archive has been successfully disabled."
    return False, f"Auto archive is still enabled (value: {auto_archive_enabled})."
