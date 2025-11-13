"""Court finder tool."""
import requests
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error


COURTS_API_URL = "https://www.find-court-tribunal.service.gov.uk/search/results.json"


def find_courts(postcode=None, name=None):
    """Find courts by postcode or name."""
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
        for court in courts_data[:20]:  # Limit to 20 results
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


def get_court_details(slug):
    """Get detailed information for a specific court."""
    try:
        response = requests.get(
            f"https://www.find-court-tribunal.service.gov.uk/courts/{slug}.json",
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Court not found"}

        response.raise_for_status()
        data = response.json()

        return {
            "name": data.get("name"),
            "types": data.get("types", []),
            "address": data.get("address"),
            "postcode": data.get("postcode"),
            "info": data.get("info"),
            "open": data.get("open"),
            "directions": data.get("directions"),
            "email": data.get("email"),
            "contacts": data.get("contacts", []),
            "opening_times": data.get("opening_times", []),
            "facilities": data.get("facilities", []),
            "areas_of_law": data.get("areas_of_law", []),
            "data_source": "Court and Tribunal Finder",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
