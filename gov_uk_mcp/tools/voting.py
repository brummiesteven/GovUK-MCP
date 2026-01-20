"""Parliamentary voting records tool."""
import requests
from datetime import datetime
from typing import Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from gov_uk_mcp.validation import sanitize_api_error


VOTES_API_URL = "https://commonsvotes-api.parliament.uk/data"

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


def _fetch_division_details(division_id: int, mp_id: int):
    """Fetch details for a single division. Helper function for concurrent execution."""
    try:
        response = requests.get(
            f"{VOTES_API_URL}/division/{division_id}.json",
            timeout=10
        )

        if response.status_code != 200:
            return None

        detail_data = response.json()

        mp_vote = None
        for vote_type in ["Ayes", "Noes"]:
            for voter in detail_data.get(vote_type, []):
                if voter.get("MemberId") == mp_id:
                    mp_vote = vote_type.lower()
                    break
            if mp_vote:
                break

        return (division_id, mp_vote, detail_data) if mp_vote else None

    except Exception:
        return None


def _get_recent_votes(mp_id: int, limit: int = 20) -> dict:
    """Get recent voting history for an MP using concurrent requests."""
    try:
        response = requests.get(
            f"{VOTES_API_URL}/divisions.json/search",
            params={"take": min(limit * 3, 100)},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        votes = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_division = {
                executor.submit(_fetch_division_details, div.get("DivisionId"), mp_id): div
                for div in data
            }

            for future in as_completed(future_to_division):
                division = future_to_division[future]
                result = future.result()

                if result:
                    division_id, mp_vote, detail_data = result
                    votes.append({
                        "division_id": division_id,
                        "title": division.get("Title"),
                        "date": division.get("Date"),
                        "vote": mp_vote,
                        "ayes_count": division.get("AyeCount"),
                        "noes_count": division.get("NoCount")
                    })

                    if len(votes) >= limit:
                        break

        if not votes:
            return {"message": "No recent votes found for this MP"}

        votes.sort(key=lambda x: x.get("date", ""), reverse=True)

        return {
            "mp_id": mp_id,
            "total_votes": len(votes),
            "votes": votes[:limit],
            "data_source": "Commons Votes API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool(meta={"ui": {"resourceUri": "ui://voting-record"}})
def get_voting_record(
    mp_name_or_id: str,
    division_id: Optional[str] = None,
    limit: int = 20
) -> dict:
    """Get voting record for an MP.

    Args:
        mp_name_or_id: MP name or member ID
        division_id: Specific division ID (optional)
        limit: Number of recent votes to return (default: 20)

    Shows how they voted on specific bills or recent voting history.
    """
    if isinstance(mp_name_or_id, str) and not mp_name_or_id.isdigit():
        from gov_uk_mcp.tools.mps import _find_mp_impl

        mp_result = _find_mp_impl(mp_name_or_id)
        if "error" in mp_result:
            return mp_result

        if "mps" in mp_result:
            return {"error": "Multiple MPs found. Please be more specific."}

        mp_id = mp_result.get("id")
    else:
        mp_id = int(mp_name_or_id) if isinstance(mp_name_or_id, str) else mp_name_or_id

    if division_id:
        try:
            response = requests.get(
                f"{VOTES_API_URL}/division/{division_id}.json",
                timeout=10
            )

            if response.status_code == 404:
                return {"error": "Division not found"}

            response.raise_for_status()
            data = response.json()

            mp_vote = None
            for vote_type in ["Ayes", "Noes"]:
                for voter in data.get(vote_type, []):
                    if voter.get("MemberId") == mp_id:
                        mp_vote = {
                            "vote": vote_type.lower(),
                            "mp_name": voter.get("Name")
                        }
                        break

            if not mp_vote:
                return {"error": "MP did not vote in this division"}

            return {
                "division_id": division_id,
                "title": data.get("Title"),
                "date": data.get("Date"),
                "mp_vote": mp_vote,
                "ayes_count": len(data.get("Ayes", [])),
                "noes_count": len(data.get("Noes", [])),
                "result": "Passed" if len(data.get("Ayes", [])) > len(data.get("Noes", [])) else "Failed",
                "data_source": "Commons Votes API",
                "retrieved_at": datetime.now().isoformat()
            }

        except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
            return sanitize_api_error(e)
    else:
        return _get_recent_votes(mp_id, limit)


@mcp.tool
def search_divisions(query: str, limit: int = 20) -> dict:
    """Search parliamentary divisions (votes) by keyword.

    Args:
        query: Search term
        limit: Number of results (default: 20)
    """
    try:
        response = requests.get(
            f"{VOTES_API_URL}/divisions.json/search",
            params={"queryParameters": query, "take": limit},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if not data:
            return {"message": "No divisions found matching your search"}

        divisions = []
        for division in data[:limit]:
            divisions.append({
                "division_id": division.get("DivisionId"),
                "title": division.get("Title"),
                "date": division.get("Date"),
                "ayes_count": division.get("AyeCount"),
                "noes_count": division.get("NoCount"),
                "passed": division.get("AyeCount", 0) > division.get("NoCount", 0)
            })

        return {
            "query": query,
            "total_results": len(divisions),
            "divisions": divisions,
            "data_source": "Commons Votes API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
