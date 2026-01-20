"""Hansard parliamentary debates search tool."""
import requests
from datetime import datetime
from typing import Optional
from gov_uk_mcp.validation import InputValidator, ValidationError, sanitize_api_error


MODERN_HANSARD_API = "https://hansard-api.parliament.uk"

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


def _search_modern_hansard(query: str, date_from: Optional[str] = None,
                           date_to: Optional[str] = None, speaker: Optional[str] = None) -> dict:
    """Search modern Hansard API (2015-present)."""
    try:
        params = {
            "searchTerm": query,
            "skip": 0,
            "take": 20
        }

        if date_from:
            params["startDate"] = date_from
        if date_to:
            params["endDate"] = date_to
        if speaker:
            params["memberName"] = speaker

        response = requests.get(
            f"{MODERN_HANSARD_API}/search/debates.json",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        results_list = data.get("Results") or data.get("results")
        if not results_list:
            return {"message": "No debates found matching your search"}

        debates = []
        for result in results_list[:20]:
            debates.append({
                "date": result.get("SittingDate") or result.get("date"),
                "house": result.get("House") or result.get("house"),
                "debate_section": result.get("DebateSection"),
                "title": result.get("Title") or result.get("subject"),
                "speaker": result.get("speaker"),
                "excerpt": result.get("excerpt"),
                "debate_id": result.get("DebateSectionExtId"),
                "url": f"{MODERN_HANSARD_API}/debates/{result.get('DebateSectionExtId')}" if result.get("DebateSectionExtId") else None
            })

        return {
            "query": query,
            "total_results": data.get("TotalResults") or data.get("totalResults") or len(debates),
            "showing": len(debates),
            "debates": debates,
            "date_range": "2015-present",
            "data_source": "Hansard API (Modern)",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool
def search_hansard(
    query: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    speaker: Optional[str] = None
) -> dict:
    """Search parliamentary debates in Hansard (2015-present).

    Args:
        query: Search term
        date_from: Start date (YYYY-MM-DD format, optional)
        date_to: End date (YYYY-MM-DD format, optional)
        speaker: Filter by speaker name (optional)

    Returns debate transcripts and speeches.
    """
    try:
        query = InputValidator.sanitize_query(query)
        if date_from:
            date_from = InputValidator.validate_date_format(date_from)
        if date_to:
            date_to = InputValidator.validate_date_format(date_to)
    except ValidationError as e:
        return {"error": str(e)}

    results = _search_modern_hansard(query, date_from, date_to, speaker)
    if date_from and int(date_from[:4]) < 2015:
        results["note"] = "Data between 2005-2015 may be limited. You're searching the modern Hansard which covers 2015 onwards."
    return results
