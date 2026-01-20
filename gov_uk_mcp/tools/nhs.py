"""NHS service finder tool."""
import requests
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error, InputValidator, ValidationError


NHS_API_URL = "https://api.nhs.uk"

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


def _get_postcode_coordinates(postcode: str):
    """Get latitude and longitude for a postcode."""
    try:
        postcode = InputValidator.validate_uk_postcode(postcode)
    except ValidationError as e:
        return None, {"error": str(e)}

    try:
        response = requests.get(
            f"https://api.postcodes.io/postcodes/{postcode}",
            timeout=10
        )

        if response.status_code == 404:
            return None, {"error": "Postcode not found"}

        response.raise_for_status()
        data = response.json()

        if data.get("status") != 200:
            return None, {"error": "Invalid postcode"}

        result = data.get("result", {})
        lat = result.get("latitude")
        lng = result.get("longitude")

        return (lat, lng), None

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return None, sanitize_api_error(e)


def _search_nhs_services(service_type: str, lat: float, lng: float, postcode: str) -> dict:
    """Search for NHS services near coordinates."""
    try:
        response = requests.get(
            f"{NHS_API_URL}/service-search/search",
            params={
                "api-version": "1",
                "search": service_type,
                "latitude": lat,
                "longitude": lng,
                "top": 10
            },
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        services = []
        for item in data.get("value", []):
            services.append({
                "name": item.get("OrganisationName"),
                "address": item.get("Address1"),
                "city": item.get("City"),
                "postcode": item.get("Postcode"),
                "phone": item.get("Contacts", {}).get("Primary"),
                "distance": item.get("Distance")
            })

        results_key = service_type.lower() + ("ies" if service_type == "Pharmacy" else "s")
        if service_type == "GP":
            results_key = "services"

        return {
            "search_postcode": postcode,
            "total_results": len(services),
            results_key: services,
            "data_source": "NHS API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool(meta={"ui": {"resourceUri": "ui://nhs-services"}})
def find_gp_surgeries(postcode: str) -> dict:
    """Find GP surgeries near a postcode.

    Args:
        postcode: UK postcode
    """
    coords, error = _get_postcode_coordinates(postcode)
    if error:
        return error

    lat, lng = coords
    return _search_nhs_services("GP", lat, lng, postcode)


@mcp.tool
def find_hospitals(postcode: str) -> dict:
    """Find hospitals near a postcode.

    Args:
        postcode: UK postcode
    """
    coords, error = _get_postcode_coordinates(postcode)
    if error:
        return error

    lat, lng = coords
    return _search_nhs_services("Hospital", lat, lng, postcode)


@mcp.tool
def find_pharmacies(postcode: str) -> dict:
    """Find pharmacies near a postcode.

    Args:
        postcode: UK postcode
    """
    coords, error = _get_postcode_coordinates(postcode)
    if error:
        return error

    lat, lng = coords
    return _search_nhs_services("Pharmacy", lat, lng, postcode)
