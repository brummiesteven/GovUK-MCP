"""Hansard parliamentary debates search tool."""
import requests
from datetime import datetime
from gov_uk_mcp.validation import InputValidator, ValidationError, sanitize_api_error


MODERN_HANSARD_API = "https://hansard-api.parliament.uk"
HISTORIC_HANSARD_API = "http://www.hansard-archive.parliament.uk"


def search_hansard(query, date_from=None, date_to=None, speaker=None):
    """Search parliamentary debates in Hansard.

    Handles both modern (2015+) and historic (pre-2005) Hansard.
    Note: Data between 2005-2015 may be limited.
    """
    try:
        query = InputValidator.sanitize_query(query)
        if date_from:
            date_from = InputValidator.validate_date_format(date_from)
        if date_to:
            date_to = InputValidator.validate_date_format(date_to)
    except ValidationError as e:
        return {"error": str(e)}

    # Determine which API to use based on dates
    if date_to and int(date_to[:4]) < 2005:
        return search_historic_hansard(query, date_from, date_to, speaker)
    elif date_from and int(date_from[:4]) >= 2015:
        return search_modern_hansard(query, date_from, date_to, speaker)
    else:
        # Search modern API and note potential gap
        results = search_modern_hansard(query, date_from, date_to, speaker)
        if date_from and int(date_from[:4]) < 2015:
            results["note"] = "Data between 2005-2015 may be limited. You're searching the modern Hansard which covers 2015 onwards."
        return results


def search_modern_hansard(query, date_from=None, date_to=None, speaker=None):
    """Search modern Hansard API (2015-present)."""
    try:
        # Note: query is already sanitized by search_hansard wrapper
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

        # API returns "Results" (capital R) not "results"
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


def search_historic_hansard(query, date_from=None, date_to=None, speaker=None):
    """Search historic Hansard (1803-2005).

    Note: Historic API returns XML and may require additional parsing.
    """
    return {
        "message": "Historic Hansard search (1803-2005) is available",
        "query": query,
        "date_range": "1803-2005",
        "note": "Historic Hansard returns XML format. For detailed historic searches, visit http://www.hansard-archive.parliament.uk/",
        "data_source": "Hansard Archive",
        "retrieved_at": datetime.now().isoformat()
    }


def get_debate_by_id(debate_id):
    """Get full details of a specific debate."""
    try:
        response = requests.get(
            f"{MODERN_HANSARD_API}/debates/{debate_id}.json",
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Debate not found"}

        response.raise_for_status()
        data = response.json()

        return {
            "id": debate_id,
            "date": data.get("date"),
            "house": data.get("house"),
            "subject": data.get("subject"),
            "contributions": data.get("contributions", []),
            "url": data.get("url"),
            "data_source": "Hansard API (Modern)",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
