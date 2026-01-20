"""Food hygiene ratings tool."""
import requests
from datetime import datetime
from typing import Optional
from gov_uk_mcp.validation import sanitize_api_error


FOOD_HYGIENE_API_URL = "https://api.ratings.food.gov.uk"

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


@mcp.tool(meta={"ui": {"resourceUri": "ui://food-hygiene"}})
def search_food_establishments(
    name: Optional[str] = None,
    postcode: Optional[str] = None,
    local_authority: Optional[str] = None
) -> dict:
    """Search for food establishments and their hygiene ratings.

    Args:
        name: Business name to search for
        postcode: Postcode to search in
        local_authority: Local authority ID
    """
    if not any([name, postcode, local_authority]):
        return {"error": "Please provide at least one search parameter (name, postcode, or local_authority)"}

    params = {}
    if name:
        params["name"] = name
    if postcode:
        # FSA API requires spaces in postcodes for accurate matching
        params["address"] = postcode.strip()
    if local_authority:
        params["localAuthorityId"] = local_authority

    try:
        response = requests.get(
            f"{FOOD_HYGIENE_API_URL}/Establishments",
            params=params,
            headers={
                "x-api-version": "2",
                "Accept": "application/json"
            },
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        establishments = data.get("establishments", [])

        if not establishments:
            return {
                "message": "No establishments found",
                "search_params": params
            }

        results = []
        for est in establishments[:20]:
            results.append({
                "business_name": est.get("BusinessName"),
                "address": est.get("AddressLine1"),
                "postcode": est.get("PostCode"),
                "local_authority": est.get("LocalAuthorityName"),
                "rating": est.get("RatingValue"),
                "rating_date": est.get("RatingDate"),
                "business_type": est.get("BusinessType"),
                "hygiene_score": est.get("scores", {}).get("Hygiene"),
                "structural_score": est.get("scores", {}).get("Structural"),
                "confidence_in_management": est.get("scores", {}).get("ConfidenceInManagement")
            })

        return {
            "total_results": len(establishments),
            "showing": len(results),
            "establishments": results,
            "data_source": "Food Standards Agency API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
