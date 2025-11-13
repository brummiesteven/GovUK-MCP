"""Schools finder tool - Note: GIAS has no public JSON API."""
from datetime import datetime


# Using the Get Information About Schools (GIAS)
GIAS_API_URL = "https://www.get-information-schools.service.gov.uk"


def find_schools(name=None, postcode=None):
    """Find schools by name or postcode.

    Note: GIAS doesn't provide a public JSON API. Full implementation requires
    downloading and parsing CSV datasets or HTML scraping.
    """
    if not name and not postcode:
        return {"error": "Please provide either a school name or postcode"}

    search_term = name or postcode

    return {
        "message": "School search requires GIAS CSV dataset or HTML parsing",
        "search_term": search_term,
        "note": "For complete school data, visit https://www.get-information-schools.service.gov.uk/",
        "limitations": "GIAS doesn't provide a public JSON API. Implementation requires CSV parsing or web scraping.",
        "alternative": f"Direct search URL: {GIAS_API_URL}/Search/Search?searchtype=establishment&search={search_term}",
        "data_source": "Get Information About Schools",
        "retrieved_at": datetime.now().isoformat()
    }


def get_school_by_urn(urn):
    """Get school details by URN (Unique Reference Number).

    Note: Returns information URL as GIAS has no public JSON API.
    """
    return {
        "message": f"School information available at GIAS website",
        "urn": urn,
        "url": f"{GIAS_API_URL}/Establishments/Establishment/Details/{urn}",
        "note": "GIAS doesn't provide a public JSON API. Visit the URL above for school details.",
        "limitations": "Full implementation requires HTML parsing or CSV dataset download.",
        "data_source": "Get Information About Schools",
        "retrieved_at": datetime.now().isoformat()
    }
