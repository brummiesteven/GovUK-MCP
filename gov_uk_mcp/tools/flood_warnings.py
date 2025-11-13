"""Flood warnings tool."""
import requests
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error


FLOOD_API_URL = "https://environment.data.gov.uk/flood-monitoring"


def get_flood_warnings(postcode=None, area=None):
    """Get active flood warnings for a postcode or area."""
    try:
        # Get all active flood warnings
        response = requests.get(
            f"{FLOOD_API_URL}/id/floods",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        items = data.get("items", [])

        if not items:
            return {"message": "No active flood warnings in England"}

        # If postcode or area provided, filter results
        if postcode or area:
            search_term = (postcode or area).upper().replace(" ", "")
            filtered = []
            for item in items:
                # Check if search term matches area description or code
                description = item.get("description", "").upper()
                area_name = item.get("eaAreaName", "").upper()
                if search_term in description or search_term in area_name:
                    filtered.append(item)
            items = filtered

        if not items:
            return {"message": f"No flood warnings for {postcode or area}"}

        warnings = []
        for item in items:
            warnings.append({
                "severity": item.get("severityLevel"),
                "severity_description": item.get("severity"),
                "area": item.get("eaAreaName"),
                "description": item.get("description"),
                "message": item.get("message"),
                "time_raised": item.get("timeRaised"),
                "time_severity_changed": item.get("timeSeverityChanged")
            })

        return {
            "total_warnings": len(warnings),
            "warnings": warnings,
            "data_source": "Environment Agency Flood Monitoring API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


def get_flood_areas():
    """Get list of all flood warning areas."""
    try:
        response = requests.get(
            f"{FLOOD_API_URL}/id/floodAreas",
            params={"_limit": 50},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        areas = []
        for item in data.get("items", []):
            areas.append({
                "area_name": item.get("label"),
                "notation": item.get("notation"),
                "county": item.get("county"),
                "river_or_sea": item.get("riverOrSea")
            })

        return {
            "areas": areas,
            "data_source": "Environment Agency Flood Monitoring API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
