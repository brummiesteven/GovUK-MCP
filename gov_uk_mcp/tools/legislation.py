"""Legislation search tool."""
import requests
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error


LEGISLATION_API_URL = "https://www.legislation.gov.uk"

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


@mcp.tool
def search_legislation(query: str, limit: int = 20) -> dict:
    """Search UK legislation by keyword.

    Args:
        query: Search query
        limit: Number of results (default: 20)
    """
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
