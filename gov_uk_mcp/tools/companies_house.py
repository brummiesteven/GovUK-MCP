"""Companies House lookup tools."""
import os
import requests
from datetime import datetime
from gov_uk_mcp.validation import InputValidator, ValidationError, sanitize_api_error


COMPANIES_HOUSE_API_URL = "https://api.company-information.service.gov.uk"

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


def _get_auth():
    """Get auth for Companies House API."""
    api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
    if not api_key:
        return None
    return (api_key, "")


@mcp.tool
def search_companies(query: str, items_per_page: int = 20) -> dict:
    """Search for UK companies by name using Companies House API.

    Args:
        query: Company name to search for
        items_per_page: Number of results to return (default: 20)
    """
    auth = _get_auth()
    if not auth:
        return {"error": "Companies House API key not configured"}

    try:
        response = requests.get(
            f"{COMPANIES_HOUSE_API_URL}/search/companies",
            params={"q": query, "items_per_page": items_per_page},
            auth=auth,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("items", []):
            results.append({
                "company_number": item.get("company_number"),
                "title": item.get("title"),
                "company_status": item.get("company_status"),
                "company_type": item.get("company_type"),
                "date_of_creation": item.get("date_of_creation"),
                "address": item.get("address", {}).get("premises"),
                "full_address": ", ".join(filter(None, [
                    item.get("address", {}).get("premises"),
                    item.get("address", {}).get("address_line_1"),
                    item.get("address", {}).get("locality"),
                    item.get("address", {}).get("postal_code")
                ]))
            })

        return {
            "total_results": data.get("total_results"),
            "companies": results,
            "data_source": "Companies House API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool(meta={"ui": {"resourceUri": "ui://company-info"}})
def get_company(company_number: str) -> dict:
    """Get detailed company information by company number from Companies House.

    Args:
        company_number: Company number (e.g., 12345678)
    """
    auth = _get_auth()
    if not auth:
        return {"error": "Companies House API key not configured"}

    try:
        company_number = InputValidator.validate_company_number(company_number)
    except ValidationError as e:
        return {"error": str(e)}

    try:
        response = requests.get(
            f"{COMPANIES_HOUSE_API_URL}/company/{company_number}",
            auth=auth,
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Company not found"}

        response.raise_for_status()
        data = response.json()

        result = {
            "company_number": data.get("company_number"),
            "company_name": data.get("company_name"),
            "company_status": data.get("company_status"),
            "company_type": data.get("company_type"),
            "date_of_creation": data.get("date_of_creation"),
            "jurisdiction": data.get("jurisdiction"),
            "registered_office_address": data.get("registered_office_address"),
            "sic_codes": data.get("sic_codes"),
            "accounts": data.get("accounts"),
            "confirmation_statement": data.get("confirmation_statement"),
            "has_insolvency_history": data.get("has_insolvency_history"),
            "has_charges": data.get("has_charges"),
            "data_source": "Companies House API",
            "retrieved_at": datetime.now().isoformat()
        }

        return result

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool
def get_company_officers(company_number: str) -> dict:
    """Get list of company officers (directors, secretaries) by company number.

    Args:
        company_number: Company number (e.g., 12345678)
    """
    auth = _get_auth()
    if not auth:
        return {"error": "Companies House API key not configured"}

    try:
        company_number = InputValidator.validate_company_number(company_number)
    except ValidationError as e:
        return {"error": str(e)}

    try:
        response = requests.get(
            f"{COMPANIES_HOUSE_API_URL}/company/{company_number}/officers",
            auth=auth,
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Company not found"}

        response.raise_for_status()
        data = response.json()

        officers = []
        for item in data.get("items", []):
            officers.append({
                "name": item.get("name"),
                "officer_role": item.get("officer_role"),
                "appointed_on": item.get("appointed_on"),
                "resigned_on": item.get("resigned_on"),
                "nationality": item.get("nationality"),
                "occupation": item.get("occupation"),
                "country_of_residence": item.get("country_of_residence"),
                "address": item.get("address")
            })

        return {
            "company_number": company_number,
            "total_officers": data.get("total_results"),
            "active_count": data.get("active_count"),
            "resigned_count": data.get("resigned_count"),
            "officers": officers,
            "data_source": "Companies House API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool
def get_company_filing_history(company_number: str, items_per_page: int = 20) -> dict:
    """Get company filing history by company number from Companies House.

    Args:
        company_number: Company number (e.g., 12345678)
        items_per_page: Number of results to return (default: 20)
    """
    auth = _get_auth()
    if not auth:
        return {"error": "Companies House API key not configured"}

    try:
        company_number = InputValidator.validate_company_number(company_number)
    except ValidationError as e:
        return {"error": str(e)}

    try:
        response = requests.get(
            f"{COMPANIES_HOUSE_API_URL}/company/{company_number}/filing-history",
            params={"items_per_page": items_per_page},
            auth=auth,
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Company not found"}

        response.raise_for_status()
        data = response.json()

        filings = []
        for item in data.get("items", []):
            filings.append({
                "date": item.get("date"),
                "category": item.get("category"),
                "description": item.get("description"),
                "type": item.get("type"),
                "action_date": item.get("action_date")
            })

        return {
            "company_number": company_number,
            "total_filings": data.get("total_count"),
            "filings": filings,
            "data_source": "Companies House API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
