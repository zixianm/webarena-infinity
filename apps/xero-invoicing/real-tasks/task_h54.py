import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Find a 45-day overdue reminder
    rem = next((r for r in state.get("invoiceReminders", [])
                if r["timing"] == "after" and r["days"] == 45), None)

    if not rem:
        return False, "No 45-day overdue reminder found."

    if not rem.get("enabled"):
        return False, "45-day reminder is not enabled."

    expected_subject = "Final notice: Invoice {InvoiceNumber} - Account referred to collections"
    if rem.get("subject") != expected_subject:
        return False, f"Subject is '{rem.get('subject')}', expected '{expected_subject}'."

    if not rem.get("includeInvoicePdf"):
        return False, "Reminder does not include invoice PDF."

    if rem.get("includeSummary"):
        return False, "Reminder should not include summary."

    return True, "45-day overdue reminder created with correct subject and settings."
