"""Charity Commission lookup tool."""
import requests
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error


CHARITY_API_URL = "https://register-of-charities.charitycommission.gov.uk/api"


def search_charities(name):
    """Search for charities by name."""
    try:
        response = requests.get(
            f"{CHARITY_API_URL}/search-charities",
            params={"q": name, "take": 20},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        charities_data = data.get("charities", [])

        if not charities_data:
            return {"message": "No charities found"}

        charities = []
        for charity in charities_data:
            charities.append({
                "charity_number": charity.get("charityNumber"),
                "charity_name": charity.get("charityName"),
                "registration_status": charity.get("registrationStatus"),
                "charity_type": charity.get("charityType"),
                "registration_date": charity.get("registrationDate"),
                "activities": charity.get("activities")
            })

        return {
            "total_results": data.get("count", len(charities)),
            "showing": len(charities),
            "charities": charities,
            "data_source": "Charity Commission Register",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


def get_charity(charity_number):
    """Get charity details by registration number."""
    try:
        response = requests.get(
            f"{CHARITY_API_URL}/charity/{charity_number}",
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Charity not found"}

        response.raise_for_status()
        data = response.json()

        return {
            "charity_number": data.get("charityNumber"),
            "charity_name": data.get("charityName"),
            "registration_status": data.get("registrationStatus"),
            "charity_type": data.get("charityType"),
            "registration_date": data.get("registrationDate"),
            "removal_date": data.get("removalDate"),
            "activities": data.get("activities"),
            "governance": data.get("governance"),
            "financial": data.get("financial"),
            "contact": data.get("contact"),
            "trustees": data.get("trustees", []),
            "data_source": "Charity Commission Register",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
