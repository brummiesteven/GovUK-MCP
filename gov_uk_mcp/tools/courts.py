"""Court finder tool."""
import requests
from datetime import datetime
from typing import Optional
from gov_uk_mcp.validation import sanitize_api_error


COURTS_API_URL = "https://www.find-court-tribunal.service.gov.uk/search/results.json"

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


@mcp.tool
def find_courts(postcode: Optional[str] = None, name: Optional[str] = None) -> dict:
    """Find courts by postcode or name.

    Args:
        postcode: UK postcode
        name: Court name to search for

    Returns court details, types, and contact information.
    """
    if not postcode and not name:
        return {"error": "Please provide either a postcode or court name"}

    try:
        params = {}
        if postcode:
            params["postcode"] = postcode.upper().replace(" ", "")
        if name:
            params["q"] = name

        response = requests.get(
            COURTS_API_URL,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        courts_data = data if isinstance(data, list) else data.get("results", [])

        if not courts_data:
            return {"message": "No courts found"}

        courts = []
        for court in courts_data[:20]:
            courts.append({
                "name": court.get("name"),
                "types": court.get("types", []),
                "address": court.get("address"),
                "postcode": court.get("postcode"),
                "distance": court.get("distance"),
                "dx_number": court.get("dx_number"),
                "image": court.get("image_file"),
                "slug": court.get("slug")
            })

        return {
            "total_results": len(courts_data),
            "showing": len(courts),
            "courts": courts,
            "data_source": "Court and Tribunal Finder",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
