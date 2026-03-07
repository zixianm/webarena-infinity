import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])

    # These are the emails that were unread + in inbox + splitCategory=="important"
    expected_subjects = {
        1: "Q2 Product Roadmap - Final Review",
        2: "Re: Series B Term Sheet Discussion",
        3: "Partnership Opportunity - FinancePlus x Acme",
        5: "Budget Approval Needed - Marketing Campaign",
        113: "Database Performance Report - March",
        114: "Accessibility Audit Results",
    }

    emails_by_id = {email.get("id"): email for email in emails}
    failures = []
    checked = 0

    for eid, expected_subject in expected_subjects.items():
        email = emails_by_id.get(eid)
        if email is None:
            failures.append(f"Email id {eid} ('{expected_subject}') not found in state.")
            continue
        checked += 1
        labels = email.get("labels", [])
        if "label_5" not in labels:
            failures.append(
                f"Email '{email.get('subject')}' (id {eid}) is missing the 'Urgent' label (label_5). "
                f"Current labels: {labels}."
            )

    if checked == 0:
        return False, "None of the expected unread Important emails were found in state."

    if failures:
        return False, " ".join(failures)

    return True, "All unread emails in the Important split now have the 'Urgent' label."
