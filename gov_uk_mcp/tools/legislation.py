"""Legislation search tool."""
import requests
import re
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error, ValidationError


LEGISLATION_API_URL = "https://www.legislation.gov.uk"


def search_legislation(query, limit=20):
    """Search UK legislation."""
    try:
        response = requests.get(
            f"{LEGISLATION_API_URL}/search",
            params={
                "q": query,
                "page": 1
            },
            headers={"Accept": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        results = []
        items = data.get("results", [])

        for item in items[:limit]:
            results.append({
                "title": item.get("title"),
                "type": item.get("type"),
                "year": item.get("year"),
                "number": item.get("number"),
                "url": item.get("url")
            })

        return {
            "query": query,
            "total_results": data.get("totalResults"),
            "showing": len(results),
            "results": results,
            "data_source": "Legislation.gov.uk",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


def get_legislation(legislation_type, year, number):
    """Get specific legislation document.

    Args:
        legislation_type: e.g., 'ukpga', 'uksi', 'asp'
        year: Year of the legislation
        number: Legislation number
    """
    # SSRF Protection: Validate all URL components
    # Validate legislation_type (only alphanumeric, lowercase, max 10 chars)
    if not re.match(r'^[a-z]{2,10}$', legislation_type):
        return {"error": "Invalid legislation type format"}

    # Validate year (1200-2100, reasonable range for UK legislation)
    try:
        year_int = int(year)
        if not (1200 <= year_int <= 2100):
            return {"error": "Year must be between 1200 and 2100"}
    except (ValueError, TypeError):
        return {"error": "Year must be a valid number"}

    # Validate number (numeric only, max 6 digits)
    if not re.match(r'^\d{1,6}$', str(number)):
        return {"error": "Legislation number must be a valid number (1-6 digits)"}

    try:
        url = f"{LEGISLATION_API_URL}/{legislation_type}/{year}/{number}"

        response = requests.get(
            url,
            headers={"Accept": "application/json"},
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Legislation not found"}

        response.raise_for_status()
        data = response.json()

        return {
            "title": data.get("title"),
            "type": legislation_type,
            "year": year,
            "number": number,
            "url": url,
            "status": data.get("status"),
            "data_source": "Legislation.gov.uk",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
