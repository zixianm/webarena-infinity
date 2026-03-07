import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    email = next((e for e in state["emails"] if e["subject"] == "Quantum Computing Integration Prototype" and e["from"]["email"] == "kevin.zhao@quantumlab.tech"), None)
    if not email:
        return False, "Email 'Quantum Computing Integration Prototype' not found."
    if not email.get("remindAt"):
        return False, "No reminder is set on the email."
    remind_at = email["remindAt"]
    if "2026-03-08" not in remind_at:
        return False, f"Reminder date should be March 8, 2026. Got: {remind_at}"
    return True, f"Reminder set for {remind_at}."
