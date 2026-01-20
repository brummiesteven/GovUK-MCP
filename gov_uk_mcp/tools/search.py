"""Gov.uk content search tool."""
import requests
from datetime import datetime
from gov_uk_mcp.validation import InputValidator, ValidationError, sanitize_api_error


SEARCH_API_URL = "https://www.gov.uk/api/search.json"

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


@mcp.tool
def search_govuk(query: str, count: int = 10) -> dict:
    """Search gov.uk content for guidance, policy documents, and other government information.

    Args:
        query: Search query
        count: Number of results to return (default: 10)
    """
    try:
        query = InputValidator.sanitize_query(query)
    except ValidationError as e:
        return {"error": str(e)}

    try:
        response = requests.get(
            SEARCH_API_URL,
            params={"q": query, "count": min(count, 50)},
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
