"""Police crime data tool."""
import requests
from datetime import datetime
from gov_uk_mcp.validation import InputValidator, ValidationError, sanitize_api_error


POLICE_API_URL = "https://data.police.uk/api"


def get_street_crime(lat, lng, date=None):
    """Get street-level crime data for a location."""
    try:
        lat, lng = InputValidator.validate_coordinates(lat, lng)
    except ValidationError as e:
        return {"error": str(e)}

    try:
        params = {"lat": lat, "lng": lng}
        if date:
            params["date"] = date

        response = requests.get(
            f"{POLICE_API_URL}/crimes-street/all-crime",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if not data:
            return {"message": "No crime data available for this location"}

        crimes = []
        for item in data[:50]:  # Limit to 50 results
            crimes.append({
                "category": item.get("category"),
                "location_type": item.get("location_type"),
                "street": item.get("location", {}).get("street", {}).get("name"),
                "month": item.get("month"),
                "outcome_status": item.get("outcome_status", {}).get("category") if item.get("outcome_status") else None
            })

        return {
            "total_crimes": len(data),
            "showing": len(crimes),
            "crimes": crimes,
            "data_source": "Police.uk API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


def get_crime_by_postcode(postcode):
    """Get crime data for a postcode area."""
    try:
        postcode = InputValidator.validate_uk_postcode(postcode)
    except ValidationError as e:
        return {"error": str(e)}

    # First need to convert postcode to coordinates using postcodes.io
    try:
        postcode_response = requests.get(
            f"https://api.postcodes.io/postcodes/{postcode}",
            timeout=10
        )

        if postcode_response.status_code == 404:
            return {"error": "Postcode not found"}

        postcode_response.raise_for_status()
        postcode_data = postcode_response.json()

        if postcode_data.get("status") != 200:
            return {"error": "Invalid postcode"}

        result = postcode_data.get("result", {})
        lat = result.get("latitude")
        lng = result.get("longitude")

        return get_street_crime(lat, lng)

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


def get_police_forces():
    """Get list of all police forces."""
    try:
        response = requests.get(f"{POLICE_API_URL}/forces", timeout=10)
        response.raise_for_status()
        data = response.json()

        forces = []
        for force in data:
            forces.append({
                "id": force.get("id"),
                "name": force.get("name")
            })

        return {
            "forces": forces,
            "data_source": "Police.uk API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


def get_force_details(force_id):
    """Get details for a specific police force."""
    try:
        response = requests.get(f"{POLICE_API_URL}/forces/{force_id}", timeout=10)

        if response.status_code == 404:
            return {"error": "Police force not found"}

        response.raise_for_status()
        data = response.json()

        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "description": data.get("description"),
            "url": data.get("url"),
            "telephone": data.get("telephone"),
            "engagement_methods": data.get("engagement_methods", []),
            "data_source": "Police.uk API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
