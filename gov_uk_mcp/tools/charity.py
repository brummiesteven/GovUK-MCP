"""Charity Commission lookup tool."""
import re
import requests
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error, ValidationError


CHARITY_API_URL = "https://register-of-charities.charitycommission.gov.uk/api"


def _validate_charity_number(charity_number: str) -> str:
    """Validate UK charity registration number format.

    UK charity numbers are typically 6-8 digits, sometimes with a suffix.
    Scottish charities use SC prefix followed by 6 digits.
    Northern Ireland charities use NIC followed by digits.
    """
    if not charity_number:
        raise ValidationError("Charity number is required")

    cleaned = charity_number.strip().upper()

    if len(cleaned) > 15:
        raise ValidationError("Charity number is too long")

    # Allow: digits only, SC+digits, NIC+digits, or digits with hyphen suffix
    if not re.match(r'^(SC\d{6}|NIC\d+|\d{6,8}(-\d+)?)$', cleaned):
        raise ValidationError(
            "Invalid charity number format. Expected 6-8 digits, "
            "SC followed by 6 digits, or NIC followed by digits"
        )

    return cleaned


def _validate_search_query(query: str, field_name: str = "Search query") -> str:
    """Validate search query input."""
    if not query:
        raise ValidationError(f"{field_name} is required")

    cleaned = query.strip()

    if len(cleaned) < 2:
        raise ValidationError(f"{field_name} must be at least 2 characters")

    if len(cleaned) > 200:
        raise ValidationError(f"{field_name} must not exceed 200 characters")

    return cleaned

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


@mcp.tool
def search_charities(name: str) -> dict:
    """Search for registered charities by name.

    Args:
        name: Charity name to search for
    """
    try:
        name = _validate_search_query(name, "Charity name")
    except ValidationError as e:
        return {"error": str(e)}

    try:
        response = requests.get(
            f"{CHARITY_API_URL}/search-charities",
            params={"q": name, "take": 20},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        charities_data = data.get("charities", [])

        if not charities_data:
            return {"message": "No charities found"}

        charities = []
        for charity in charities_data:
            charities.append({
                "charity_number": charity.get("charityNumber"),
                "charity_name": charity.get("charityName"),
                "registration_status": charity.get("registrationStatus"),
                "charity_type": charity.get("charityType"),
                "registration_date": charity.get("registrationDate"),
                "activities": charity.get("activities")
            })

        return {
            "total_results": data.get("count", len(charities)),
            "showing": len(charities),
            "charities": charities,
            "data_source": "Charity Commission Register",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool(meta={"ui": {"resourceUri": "ui://charity-info"}})
def get_charity(charity_number: str) -> dict:
    """Get detailed charity information by registration number.

    Args:
        charity_number: Charity registration number
    """
    try:
        charity_number = _validate_charity_number(charity_number)
    except ValidationError as e:
        return {"error": str(e)}

    try:
        response = requests.get(
            f"{CHARITY_API_URL}/charity/{charity_number}",
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Charity not found"}

        response.raise_for_status()
        data = response.json()

        return {
            "charity_number": data.get("charityNumber"),
            "charity_name": data.get("charityName"),
            "registration_status": data.get("registrationStatus"),
            "charity_type": data.get("charityType"),
            "registration_date": data.get("registrationDate"),
            "removal_date": data.get("removalDate"),
            "activities": data.get("activities"),
            "governance": data.get("governance"),
            "financial": data.get("financial"),
            "contact": data.get("contact"),
            "trustees": data.get("trustees", []),
            "data_source": "Charity Commission Register",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
