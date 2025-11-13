"""Bank holidays tool."""
import requests
from datetime import datetime, date
from gov_uk_mcp.validation import sanitize_api_error


BANK_HOLIDAYS_URL = "https://www.gov.uk/bank-holidays.json"


def get_bank_holidays(country=None):
    """Get UK bank holidays.

    Args:
        country: Optional filter for specific country (england-and-wales, scotland, northern-ireland)
    """
    try:
        response = requests.get(BANK_HOLIDAYS_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        today = date.today()

        if country:
            country_key = country.lower().replace(" ", "-")
            if country_key not in data:
                return {"error": f"Invalid country. Choose from: {', '.join(data.keys())}"}

            events = data[country_key].get("events", [])

            # Filter for upcoming holidays
            upcoming = [
                event for event in events
                if datetime.strptime(event["date"], "%Y-%m-%d").date() >= today
            ]

            return {
                "country": country_key,
                "upcoming_holidays": upcoming,
                "data_source": "GOV.UK Bank Holidays API",
                "retrieved_at": datetime.now().isoformat()
            }

        # Return all countries
        result = {}
        for country_key, country_data in data.items():
            events = country_data.get("events", [])
            upcoming = [
                event for event in events
                if datetime.strptime(event["date"], "%Y-%m-%d").date() >= today
            ]
            result[country_key] = {
                "division": country_data.get("division"),
                "upcoming_holidays": upcoming
            }

        result["data_source"] = "GOV.UK Bank Holidays API"
        result["retrieved_at"] = datetime.now().isoformat()

        return result

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
