"""MP lookup tool."""
import re
import requests
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error


MEMBERS_API_URL = "https://members-api.parliament.uk/api"


def looks_like_postcode(query):
    """Check if query looks like a UK postcode."""
    query = query.upper().replace(" ", "")
    # UK postcode pattern
    pattern = r'^[A-Z]{1,2}[0-9][A-Z0-9]?[0-9][A-Z]{2}$'
    return bool(re.match(pattern, query))


def get_constituency_from_postcode(postcode):
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


def find_mp(query):
    """Find MP by name, constituency, or postcode."""
    # Check if it's a postcode
    if looks_like_postcode(query):
        constituency = get_constituency_from_postcode(query)
        if not constituency:
            return {"error": "Could not find constituency for this postcode"}

        # Search for MP by constituency
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

            # Get current MP for this constituency
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

            return format_mp_details(mp)

        except requests.Timeout:
            return {"error": "Request timed out"}
        except requests.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}

    # Otherwise search by name or constituency
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
            results.append(format_mp_details(mp))

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


def format_mp_details(mp):
    """Format MP details into a clean structure."""
    return {
        "id": mp.get("id"),
        "name": mp.get("nameDisplayAs"),
        "party": mp.get("latestParty", {}).get("name"),
        "constituency": mp.get("latestHouseMembership", {}).get("membershipFrom"),
        "membership_start": mp.get("latestHouseMembership", {}).get("membershipStartDate"),
        "gender": mp.get("gender"),
        "thumbnail_url": mp.get("thumbnailUrl"),
        "data_source": "UK Parliament Members API",
        "retrieved_at": datetime.now().isoformat()
    }


def get_mp_details(mp_id):
    """Get detailed information for a specific MP."""
    try:
        response = requests.get(
            f"{MEMBERS_API_URL}/Members/{mp_id}",
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "MP not found"}

        response.raise_for_status()
        data = response.json()
        mp = data.get("value", {})

        return {
            "id": mp.get("id"),
            "name": mp.get("nameDisplayAs"),
            "full_title": mp.get("nameFullTitle"),
            "party": mp.get("latestParty", {}).get("name"),
            "constituency": mp.get("latestHouseMembership", {}).get("membershipFrom"),
            "membership_start": mp.get("latestHouseMembership", {}).get("membershipStartDate"),
            "gender": mp.get("gender"),
            "date_of_birth": mp.get("dateOfBirth"),
            "date_of_death": mp.get("dateOfDeath"),
            "thumbnail_url": mp.get("thumbnailUrl"),
            "data_source": "UK Parliament Members API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


def get_mp_contact(mp_id):
    """Get contact details for an MP."""
    try:
        response = requests.get(
            f"{MEMBERS_API_URL}/Members/{mp_id}/Contact",
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "MP not found"}

        response.raise_for_status()
        data = response.json()

        contacts = []
        for contact in data.get("value", []):
            contacts.append({
                "type": contact.get("type"),
                "line1": contact.get("line1"),
                "line2": contact.get("line2"),
                "postcode": contact.get("postcode"),
                "phone": contact.get("phone"),
                "email": contact.get("email")
            })

        return {
            "mp_id": mp_id,
            "contacts": contacts,
            "data_source": "UK Parliament Members API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
