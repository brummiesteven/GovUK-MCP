"""Care Quality Commission (CQC) ratings tool."""
import requests
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error, InputValidator, ValidationError


CQC_API_URL = "https://api.cqc.org.uk/public/v1"


def search_cqc_providers(name=None, postcode=None):
    """Search for CQC registered care providers."""
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
        for loc in locations[:20]:  # Limit to 20 results
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


def get_cqc_provider(location_id):
    """Get detailed information for a CQC provider."""
    try:
        # Validate location_id to prevent injection attacks
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
