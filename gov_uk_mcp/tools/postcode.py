"""Postcode lookup tool."""
import requests
from datetime import datetime
from gov_uk_mcp.validation import InputValidator, ValidationError, sanitize_api_error


POSTCODES_API_URL = "https://api.postcodes.io"

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


@mcp.tool(meta={"ui": {"resourceUri": "ui://postcode-lookup"}})
def lookup_postcode(postcode: str) -> dict:
    """Look up details for a UK postcode.

    Args:
        postcode: UK postcode (e.g., SW1A 1AA)

    Returns location, council, constituency, and coordinates.
    """
    try:
        postcode = InputValidator.validate_uk_postcode(postcode)
    except ValidationError as e:
        return {"error": str(e)}

    try:
        response = requests.get(
            f"{POSTCODES_API_URL}/postcodes/{postcode}",
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Postcode not found"}

        response.raise_for_status()
        data = response.json()

        if data.get("status") != 200:
            return {"error": "Invalid postcode"}

        result_data = data.get("result", {})

        result = {
            "postcode": result_data.get("postcode"),
            "latitude": result_data.get("latitude"),
            "longitude": result_data.get("longitude"),
            "admin_district": result_data.get("admin_district"),
            "parliamentary_constituency": result_data.get("parliamentary_constituency"),
            "region": result_data.get("region"),
            "country": result_data.get("country"),
            "european_electoral_region": result_data.get("european_electoral_region"),
            "primary_care_trust": result_data.get("primary_care_trust"),
            "ward": result_data.get("admin_ward"),
            "parish": result_data.get("parish"),
            "codes": {
                "admin_district": result_data.get("codes", {}).get("admin_district"),
                "admin_county": result_data.get("codes", {}).get("admin_county"),
                "admin_ward": result_data.get("codes", {}).get("admin_ward"),
                "parish": result_data.get("codes", {}).get("parish"),
                "parliamentary_constituency": result_data.get("codes", {}).get("parliamentary_constituency"),
                "ccg": result_data.get("codes", {}).get("ccg")
            },
            "data_source": "Postcodes.io API",
            "retrieved_at": datetime.now().isoformat()
        }

        return result

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool
def nearest_postcodes(postcode: str, limit: int = 10) -> dict:
    """Find nearest postcodes to a given postcode.

    Args:
        postcode: UK postcode (e.g., SW1A 1AA)
        limit: Number of nearest postcodes to return (default: 10)
    """
    try:
        postcode = InputValidator.validate_uk_postcode(postcode)
    except ValidationError as e:
        return {"error": str(e)}

    try:
        response = requests.get(
            f"{POSTCODES_API_URL}/postcodes/{postcode}/nearest",
            params={"limit": limit},
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Postcode not found"}

        response.raise_for_status()
        data = response.json()

        if data.get("status") != 200:
            return {"error": "Invalid postcode"}

        postcodes = []
        for item in data.get("result", []):
            postcodes.append({
                "postcode": item.get("postcode"),
                "distance": item.get("distance"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "admin_district": item.get("admin_district")
            })

        return {
            "search_postcode": postcode,
            "nearest_postcodes": postcodes,
            "data_source": "Postcodes.io API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
