"""MP lookup tool."""
import re
import base64
import requests
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error


MEMBERS_API_URL = "https://members-api.parliament.uk/api"


def _fetch_thumbnail_as_base64(url: str) -> str | None:
    """Fetch thumbnail and convert to base64 data URL to avoid CORS issues."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "image/jpeg")
            b64 = base64.b64encode(response.content).decode("utf-8")
            return f"data:{content_type};base64,{b64}"
    except requests.RequestException:
        pass
    return None

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


def _looks_like_postcode(query: str) -> bool:
    """Check if query looks like a UK postcode."""
    query = query.upper().replace(" ", "")
    pattern = r'^[A-Z]{1,2}[0-9][A-Z0-9]?[0-9][A-Z]{2}$'
    return bool(re.match(pattern, query))


def _get_constituency_from_postcode(postcode: str):
    """Get constituency from postcode using postcodes.io."""
    try:
        response = requests.get(
            f"https://api.postcodes.io/postcodes/{postcode}",
            timeout=10
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        data = response.json()

        if data.get("status") != 200:
            return None

        return data.get("result", {}).get("parliamentary_constituency")

    except requests.RequestException:
        return None


def _format_mp_details(mp: dict) -> dict:
    """Format MP details into a clean structure."""
    # Convert thumbnail to base64 data URL to avoid CORS issues in widgets
    thumbnail_url = mp.get("thumbnailUrl")
    thumbnail_data = None
    if thumbnail_url:
        thumbnail_data = _fetch_thumbnail_as_base64(thumbnail_url)

    return {
        "id": mp.get("id"),
        "name": mp.get("nameDisplayAs"),
        "party": mp.get("latestParty", {}).get("name"),
        "constituency": mp.get("latestHouseMembership", {}).get("membershipFrom"),
        "membership_start": mp.get("latestHouseMembership", {}).get("membershipStartDate"),
        "gender": mp.get("gender"),
        "thumbnail_url": thumbnail_data,  # Now a base64 data URL
        "data_source": "UK Parliament Members API",
        "retrieved_at": datetime.now().isoformat()
    }


def _find_mp_impl(query: str) -> dict:
    """Internal implementation - Find MP by name, constituency, or postcode.

    This is the actual implementation that can be called by other tools.
    Use find_mp() for the MCP tool interface.
    """
    if _looks_like_postcode(query):
        constituency = _get_constituency_from_postcode(query)
        if not constituency:
            return {"error": "Could not find constituency for this postcode"}

        try:
            response = requests.get(
                f"{MEMBERS_API_URL}/Location/Constituency/Search",
                params={"searchText": constituency, "skip": 0, "take": 1},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            if not items or len(items) == 0:
                return {"error": f"No MP found for constituency: {constituency}"}

            constituency_id = items[0]["value"]["id"]

            mp_response = requests.get(
                f"{MEMBERS_API_URL}/Members/Search",
                params={
                    "ConstituencyId": constituency_id,
                    "IsCurrentMember": True,
                    "skip": 0,
                    "take": 1
                },
                timeout=10
            )
            mp_response.raise_for_status()
            mp_data = mp_response.json()

            mp_items = mp_data.get("items", [])
            if not mp_items or len(mp_items) == 0:
                return {"error": f"No current MP found for {constituency}"}

            mp = mp_items[0]["value"]

            return _format_mp_details(mp)

        except requests.Timeout:
            return {"error": "Request timed out"}
        except requests.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}

    try:
        response = requests.get(
            f"{MEMBERS_API_URL}/Members/Search",
            params={"Name": query, "IsCurrentMember": True, "skip": 0, "take": 10},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("items"):
            return {"error": f"No MPs found matching: {query}"}

        results = []
        for item in data["items"]:
            mp = item["value"]
            results.append(_format_mp_details(mp))

        if len(results) == 1:
            return results[0]

        return {
            "total_results": len(results),
            "mps": results,
            "data_source": "UK Parliament Members API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool(meta={"ui": {"resourceUri": "ui://mp-info"}})
def find_mp(query: str) -> dict:
    """Find MP by name, constituency, or postcode.

    Args:
        query: MP name, constituency name, or UK postcode

    Returns MP details including party and constituency.
    """
    return _find_mp_impl(query)
