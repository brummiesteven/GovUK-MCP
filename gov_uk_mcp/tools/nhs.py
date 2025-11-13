"""NHS service finder tool."""
import requests
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error

# Using NHS API (requires registration at https://digital.nhs.uk/)
NHS_API_URL = "https://api.nhs.uk"


def _get_postcode_coordinates(postcode):
    """Get latitude and longitude for a postcode.

    Args:
        postcode: UK postcode

    Returns:
        Tuple of (latitude, longitude) or (None, None) with error dict on failure
    """
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


def _search_nhs_services(service_type, lat, lng, postcode):
    """Search for NHS services near coordinates.

    Args:
        service_type: Type of service ('GP', 'Hospital', 'Pharmacy')
        lat: Latitude
        lng: Longitude
        postcode: Original postcode searched

    Returns:
        Dictionary with search results or error
    """
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

        # Determine the results key based on service type
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


def find_gp_surgeries(postcode):
    """Find GP surgeries near a postcode."""
    coords, error = _get_postcode_coordinates(postcode)
    if error:
        return error

    lat, lng = coords
    return _search_nhs_services("GP", lat, lng, postcode)


def find_hospitals(postcode):
    """Find hospitals near a postcode."""
    coords, error = _get_postcode_coordinates(postcode)
    if error:
        return error

    lat, lng = coords
    return _search_nhs_services("Hospital", lat, lng, postcode)


def find_pharmacies(postcode):
    """Find pharmacies near a postcode."""
    coords, error = _get_postcode_coordinates(postcode)
    if error:
        return error

    lat, lng = coords
    return _search_nhs_services("Pharmacy", lat, lng, postcode)
