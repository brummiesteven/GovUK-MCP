"""Flood warnings tool."""
import requests
from datetime import datetime
from typing import Optional
from gov_uk_mcp.validation import sanitize_api_error


FLOOD_API_URL = "https://environment.data.gov.uk/flood-monitoring"

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


@mcp.tool(meta={"ui": {"resourceUri": "ui://flood-warnings"}})
def get_flood_warnings(postcode: Optional[str] = None, area: Optional[str] = None) -> dict:
    """Get active flood warnings for England. Can filter by postcode or area.

    Args:
        postcode: Postcode to search for (optional)
        area: Area name to search for (optional)
    """
    try:
        response = requests.get(
            f"{FLOOD_API_URL}/id/floods",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        items = data.get("items", [])

        if not items:
            return {"message": "No active flood warnings in England"}

        if postcode or area:
            search_term = (postcode or area).upper().replace(" ", "")
            filtered = []
            for item in items:
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
