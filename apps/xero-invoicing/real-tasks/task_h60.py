import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Check that no repeating invoices have saveAs = "approved_for_sending"
    auto_send = [ri for ri in state.get("repeatingInvoices", [])
                 if ri.get("saveAs") == "approved_for_sending"]

    if auto_send:
        names = ", ".join(ri["id"] for ri in auto_send)
        return False, f"{len(auto_send)} repeating invoice(s) still set to auto-send: {names}."

    # Verify that the ones that were approved_for_sending are now draft
    # rep_001 (Greenfield) and rep_003 (Cascade) were approved_for_sending in seed
    for rep_id in ["rep_001", "rep_003"]:
        ri = next((r for r in state["repeatingInvoices"] if r["id"] == rep_id), None)
        if ri and ri.get("saveAs") != "draft":
            return False, f"{rep_id} saveAs is '{ri.get('saveAs')}', expected 'draft'."

    return True, "All auto-send repeating invoices changed to save as draft."
