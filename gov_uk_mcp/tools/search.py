"""Gov.uk content search tool."""
import requests
from datetime import datetime
from gov_uk_mcp.validation import InputValidator, ValidationError, sanitize_api_error


SEARCH_API_URL = "https://www.gov.uk/api/search.json"


def search_govuk(query, count=10):
    """Search gov.uk content.

    Args:
        query: Search query string
        count: Number of results to return (max 1500)
    """
    try:
        query = InputValidator.sanitize_query(query)
    except ValidationError as e:
        return {"error": str(e)}

    try:
        response = requests.get(
            SEARCH_API_URL,
            params={"q": query, "count": min(count, 50)},  # Limit to 50 for practicality
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("results", []):
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "description": item.get("description"),
                "public_timestamp": item.get("public_timestamp"),
                "format": item.get("format"),
                "organisation": item.get("organisations", [{}])[0].get("title") if item.get("organisations") else None,
                "content_purpose_supergroup": item.get("content_purpose_supergroup")
            })

        return {
            "query": query,
            "total_results": data.get("total"),
            "showing": len(results),
            "results": results,
            "data_source": "GOV.UK Search API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
