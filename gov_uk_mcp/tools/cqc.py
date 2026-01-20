"""Care Quality Commission (CQC) ratings tool."""
import requests
from datetime import datetime
from typing import Optional
from gov_uk_mcp.validation import sanitize_api_error, InputValidator, ValidationError


CQC_API_URL = "https://api.cqc.org.uk/public/v1"

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


@mcp.tool
def search_cqc_providers(name: Optional[str] = None, postcode: Optional[str] = None) -> dict:
    """Search for CQC registered care providers by name or postcode.

    Args:
        name: Provider name
        postcode: UK postcode
    """
    if not name and not postcode:
        return {"error": "Please provide either a provider name or postcode"}

    try:
        params = {"partnerId": "gov-uk-mcp"}

        if name:
            params["name"] = name
        if postcode:
            params["postcode"] = postcode.upper().replace(" ", "")

        response = requests.get(
            f"{CQC_API_URL}/locations",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        locations = data.get("locations", [])

        if not locations:
            return {"message": "No CQC providers found"}

        providers = []
        for loc in locations[:20]:
            providers.append({
                "location_id": loc.get("locationId"),
                "name": loc.get("name"),
                "type": loc.get("type"),
                "address": loc.get("postalAddressLine1"),
                "postcode": loc.get("postalCode"),
                "overall_rating": loc.get("currentRatings", {}).get("overall", {}).get("rating"),
                "inspection_date": loc.get("lastInspection", {}).get("date")
            })

        return {
            "total_results": len(locations),
            "showing": len(providers),
            "providers": providers,
            "data_source": "Care Quality Commission API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool(meta={"ui": {"resourceUri": "ui://cqc-rating"}})
def get_cqc_provider(location_id: str) -> dict:
    """Get detailed CQC ratings and information for a care provider.

    Args:
        location_id: CQC location ID
    """
    try:
        location_id = InputValidator.validate_cqc_location_id(location_id)
    except ValidationError as e:
        return {"error": str(e)}

    try:
        response = requests.get(
            f"{CQC_API_URL}/locations/{location_id}",
            params={"partnerId": "gov-uk-mcp"},
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Provider not found"}

        response.raise_for_status()
        data = response.json()

        ratings = data.get("currentRatings", {})

        return {
            "location_id": data.get("locationId"),
            "name": data.get("name"),
            "type": data.get("type"),
            "address": {
                "line1": data.get("postalAddressLine1"),
                "line2": data.get("postalAddressLine2"),
                "town": data.get("postalAddressTownCity"),
                "county": data.get("postalAddressCounty"),
                "postcode": data.get("postalCode")
            },
            "phone": data.get("mainPhoneNumber"),
            "overall_rating": ratings.get("overall", {}).get("rating"),
            "ratings": {
                "safe": ratings.get("safe", {}).get("rating"),
                "effective": ratings.get("effective", {}).get("rating"),
                "caring": ratings.get("caring", {}).get("rating"),
                "responsive": ratings.get("responsive", {}).get("rating"),
                "well_led": ratings.get("wellLed", {}).get("rating")
            },
            "inspection_date": data.get("lastInspection", {}).get("date"),
            "registration_status": data.get("registrationStatus"),
            "data_source": "Care Quality Commission API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
