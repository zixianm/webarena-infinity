import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # INV-0049 is Coastal Living Interiors' invoice using Simple Clean template
    src = next((i for i in state["invoices"] if i["number"] == "INV-0049"), None)
    if not src:
        return False, "Source invoice INV-0049 not found."

    # Find a new draft invoice with same contact and total but Professional Services theme
    new_inv = next((i for i in state["invoices"]
                    if i["contactId"] == src["contactId"]
                    and i["number"] != "INV-0049"
                    and abs(i["total"] - src["total"]) < 0.01
                    and i["brandingThemeId"] == "theme_professional"), None)

    if not new_inv:
        return False, "No copy of INV-0049 with Professional Services theme found."

    if len(new_inv.get("lineItems", [])) != len(src.get("lineItems", [])):
        return False, f"Copy has {len(new_inv['lineItems'])} line items, expected {len(src['lineItems'])}."

    return True, f"INV-0049 duplicated as {new_inv['number']} with Professional Services theme."
