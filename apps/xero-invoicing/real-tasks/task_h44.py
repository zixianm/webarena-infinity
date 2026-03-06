import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    theme = next((t for t in state["brandingThemes"] if t["id"] == "theme_retail"), None)
    if not theme:
        return False, "Retail branding theme not found."

    if theme.get("showTaxNumber") is not False:
        return False, f"Retail showTaxNumber is {theme.get('showTaxNumber')}, expected False."

    if theme.get("showPaymentAdvice") is not True:
        return False, f"Retail showPaymentAdvice is {theme.get('showPaymentAdvice')}, expected True."

    return True, "Retail theme updated: ABN hidden, payment advice shown."
