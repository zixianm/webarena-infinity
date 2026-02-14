import requests

def verify(server_url: str) -> tuple[bool, str]:
    """Verify: customer 'NovaTech' (novatech.io, Business), CS issue 'NovaTech onboarding setup', linked request."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Check customer
    customer = next((c for c in state.get("customers", []) if c.get("name") == "NovaTech"), None)
    if not customer:
        errors.append("Customer 'NovaTech' not found.")
    else:
        if customer.get("domain") != "novatech.io":
            errors.append(f"Expected domain 'novatech.io', got '{customer.get('domain')}'.")
        if customer.get("tier") != "Business":
            errors.append(f"Expected tier 'Business', got '{customer.get('tier')}'.")

    # Check issue
    issue = next((i for i in state.get("issues", []) if i.get("title") == "NovaTech onboarding setup"), None)
    if not issue:
        errors.append("Issue 'NovaTech onboarding setup' not found.")
    else:
        if issue.get("teamId") != "team-4":
            errors.append(f"Expected team 'team-4' (Customer Success), got '{issue.get('teamId')}'.")

    # Check customer request
    if customer and issue:
        request = next((cr for cr in state.get("customerRequests", [])
                        if cr.get("customerId") == customer.get("id")
                        and cr.get("issueId") == issue.get("id")), None)
        if not request:
            errors.append("No customer request found linking NovaTech to the issue.")
        else:
            if "onboarding" not in (request.get("title") or "").lower():
                errors.append(f"Expected request title to contain 'onboarding', got '{request.get('title')}'.")

    if errors:
        return False, " | ".join(errors)

    return True, "Customer NovaTech, CS issue, and linked request all created correctly."
