"""Energy Performance Certificate (EPC) lookup tool."""
import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from gov_uk_mcp.validation import InputValidator, ValidationError, sanitize_api_error


EPC_API_URL = "https://epc.opendatacommunities.org/api/v1"


def _get_auth(api_key):
    """Create HTTPBasicAuth for EPC API.

    EPC API uses email:api_key format for Basic Auth.
    If api_key contains ':', split into username/password.
    Otherwise use api_key as username with empty password.
    """
    if ":" in api_key:
        username, password = api_key.split(":", 1)
        return HTTPBasicAuth(username, password)
    else:
        return HTTPBasicAuth(api_key, "")


def search_epc_by_postcode(postcode):
    """Search for EPCs by postcode."""
    api_key = os.getenv("EPC_API_KEY")
    if not api_key:
        return {"error": "EPC API key not configured"}

    try:
        postcode = InputValidator.validate_uk_postcode(postcode)
        # Remove spaces for EPC API
        postcode = postcode.replace(" ", "")
    except ValidationError as e:
        return {"error": str(e)}

    try:
        response = requests.get(
            f"{EPC_API_URL}/domestic/search",
            params={"postcode": postcode},
            headers={"Accept": "application/json"},
            auth=_get_auth(api_key),
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "No EPCs found for this postcode"}

        response.raise_for_status()
        data = response.json()

        rows = data.get("rows", [])
        if not rows:
            return {"message": "No EPCs found for this postcode"}

        certificates = []
        for row in rows[:20]:  # Limit to 20 results
            certificates.append({
                "address": row.get("address"),
                "postcode": row.get("postcode"),
                "current_energy_rating": row.get("current-energy-rating"),
                "potential_energy_rating": row.get("potential-energy-rating"),
                "current_energy_efficiency": row.get("current-energy-efficiency"),
                "potential_energy_efficiency": row.get("potential-energy-efficiency"),
                "property_type": row.get("property-type"),
                "built_form": row.get("built-form"),
                "inspection_date": row.get("inspection-date"),
                "lodgement_date": row.get("lodgement-date"),
                "total_floor_area": row.get("total-floor-area"),
                "environmental_impact_current": row.get("environmental-impact-current"),
                "environmental_impact_potential": row.get("environmental-impact-potential")
            })

        return {
            "total_results": len(rows),
            "showing": len(certificates),
            "certificates": certificates,
            "data_source": "EPC Open Data Communities API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


def get_epc_recommendations(certificate_id):
    """Get improvement recommendations for a specific EPC."""
    try:
        # Validate certificate_id to prevent injection attacks
        certificate_id = InputValidator.validate_epc_certificate_id(certificate_id)
    except ValidationError as e:
        return {"error": str(e)}

    api_key = os.getenv("EPC_API_KEY")
    if not api_key:
        return {"error": "EPC API key not configured"}

    try:
        response = requests.get(
            f"{EPC_API_URL}/domestic/certificate/{certificate_id}",
            headers={"Accept": "application/json"},
            auth=_get_auth(api_key),
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Certificate not found"}

        response.raise_for_status()
        data = response.json()

        rows = data.get("rows", [])
        if not rows:
            return {"error": "Certificate not found"}

        cert = rows[0]

        return {
            "address": cert.get("address"),
            "current_rating": cert.get("current-energy-rating"),
            "potential_rating": cert.get("potential-energy-rating"),
            "main_heating": cert.get("main-heating"),
            "main_fuel": cert.get("main-fuel"),
            "walls_description": cert.get("walls-description"),
            "roof_description": cert.get("roof-description"),
            "windows_description": cert.get("windows-description"),
            "data_source": "EPC Open Data Communities API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
