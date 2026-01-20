"""Transport status tool."""
import os
import re
import requests
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error, InputValidator, ValidationError
from typing import Optional


def _validate_location(location: str, field_name: str = "Location") -> str:
    """Validate location input for journey planning."""
    if not location:
        raise ValidationError(f"{field_name} is required")

    cleaned = location.strip()

    if len(cleaned) < 2:
        raise ValidationError(f"{field_name} must be at least 2 characters")

    if len(cleaned) > 200:
        raise ValidationError(f"{field_name} must not exceed 200 characters")

    # Check for potentially dangerous characters that could be used in path traversal
    if re.search(r'[<>"\']', cleaned):
        raise ValidationError(f"{field_name} contains invalid characters")

    return cleaned


TFL_API_URL = "https://api.tfl.gov.uk"

# Import mcp after defining constants to avoid circular import at module level
def _get_mcp():
    from gov_uk_mcp.server import mcp
    return mcp

mcp = _get_mcp()


@mcp.tool(meta={"ui": {"resourceUri": "ui://tube-status"}})
def get_tube_status() -> dict:
    """Get current status of all London Underground lines.

    Returns status, delays, and disruption info for all tube lines.
    """
    api_key = os.getenv("TFL_API_KEY")

    try:
        params = {}
        if api_key:
            params["app_key"] = api_key

        response = requests.get(
            f"{TFL_API_URL}/Line/Mode/tube/Status",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        lines = []
        for line in data:
            status = line.get("lineStatuses", [{}])[0]
            lines.append({
                "line": line.get("name"),
                "status": status.get("statusSeverityDescription"),
                "reason": status.get("reason"),
                "disruption": status.get("disruption")
            })

        return {
            "lines": lines,
            "data_source": "Transport for London API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool
def get_line_status(line_id: str) -> dict:
    """Get status for a specific London Underground line.

    Args:
        line_id: Line ID (e.g., 'central', 'northern', 'piccadilly')
    """
    try:
        line_id = InputValidator.validate_tfl_line_id(line_id)
    except ValidationError as e:
        return {"error": str(e)}

    api_key = os.getenv("TFL_API_KEY")

    try:
        params = {}
        if api_key:
            params["app_key"] = api_key

        response = requests.get(
            f"{TFL_API_URL}/Line/{line_id}/Status",
            params=params,
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Line not found"}

        response.raise_for_status()
        data = response.json()

        if not data or len(data) == 0:
            return {"error": "Line not found"}

        line = data[0]
        line_statuses = line.get("lineStatuses", [])
        status = line_statuses[0] if line_statuses else {}

        return {
            "line": line.get("name"),
            "status": status.get("statusSeverityDescription"),
            "reason": status.get("reason"),
            "disruption": status.get("disruption"),
            "data_source": "Transport for London API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool(meta={"ui": {"resourceUri": "ui://journey-planner"}})
def plan_journey(
    from_location: str,
    to_location: str,
    via: Optional[str] = None,
    time: Optional[str] = None,
    time_is_arrival: bool = False
) -> dict:
    """Plan a journey between two locations in London using public transport.

    Args:
        from_location: Starting point (postcode, station name, or address)
        to_location: Destination (postcode, station name, or address)
        via: Optional intermediate stop
        time: Optional time for journey (ISO format or HH:MM)
        time_is_arrival: If True, time is arrival time; if False, departure time
    """
    try:
        from_location = _validate_location(from_location, "Starting location")
        to_location = _validate_location(to_location, "Destination")
        if via:
            via = _validate_location(via, "Via location")
    except ValidationError as e:
        return {"error": str(e)}

    api_key = os.getenv("TFL_API_KEY")

    try:
        params = {}
        if api_key:
            params["app_key"] = api_key

        if via:
            params["via"] = via
        if time:
            params["time"] = time
            params["timeIs"] = "Arriving" if time_is_arrival else "Departing"

        response = requests.get(
            f"{TFL_API_URL}/Journey/JourneyResults/{from_location}/to/{to_location}",
            params=params,
            timeout=15
        )

        if response.status_code == 300:
            return {"error": "Multiple locations found. Please be more specific."}

        if response.status_code == 404:
            return {"error": "Location not found"}

        response.raise_for_status()
        data = response.json()

        journeys = []
        for journey in data.get("journeys", [])[:5]:
            legs = []
            for leg in journey.get("legs", []):
                legs.append({
                    "mode": leg.get("mode", {}).get("name"),
                    "duration": leg.get("duration"),
                    "departure_point": leg.get("departurePoint", {}).get("commonName"),
                    "arrival_point": leg.get("arrivalPoint", {}).get("commonName"),
                    "departure_time": leg.get("departureTime"),
                    "arrival_time": leg.get("arrivalTime"),
                    "instruction": leg.get("instruction", {}).get("summary")
                })

            journeys.append({
                "duration": journey.get("duration"),
                "start_time": journey.get("startDateTime"),
                "arrival_time": journey.get("arrivalDateTime"),
                "legs": legs
            })

        return {
            "from": from_location,
            "to": to_location,
            "journey_options": journeys,
            "data_source": "Transport for London API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool(meta={"ui": {"resourceUri": "ui://bike-points"}})
def get_bike_points(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius: int = 500
) -> dict:
    """Get Santander Cycles docking stations in London.

    Args:
        lat: Latitude for location search (optional)
        lon: Longitude for location search (required if lat provided)
        radius: Search radius in meters (default: 500)
    """
    api_key = os.getenv("TFL_API_KEY")

    try:
        params = {}
        if api_key:
            params["app_key"] = api_key

        if lat is not None and lon is not None:
            response = requests.get(
                f"{TFL_API_URL}/BikePoint",
                params={**params, "lat": lat, "lon": lon, "radius": radius},
                timeout=10
            )
        else:
            response = requests.get(
                f"{TFL_API_URL}/BikePoint",
                params=params,
                timeout=10
            )

        response.raise_for_status()
        data = response.json()

        # Handle different response formats:
        # - With lat/lon: {"places": [...]}
        # - Without: direct list [...]
        if isinstance(data, dict):
            points_list = data.get("places", [])
        else:
            points_list = data

        bike_points = []
        for point in points_list[:20]:
            properties = {}
            for prop in point.get("additionalProperties", []):
                key = prop.get("key")
                value = prop.get("value")
                if key in ["NbBikes", "NbEmptyDocks", "NbDocks"]:
                    properties[key] = value

            bike_points.append({
                "id": point.get("id"),
                "name": point.get("commonName"),
                "lat": point.get("lat"),
                "lon": point.get("lon"),
                "bikes_available": properties.get("NbBikes"),
                "empty_docks": properties.get("NbEmptyDocks"),
                "total_docks": properties.get("NbDocks")
            })

        return {
            "total_results": len(points_list),
            "showing": len(bike_points),
            "bike_points": bike_points,
            "data_source": "Transport for London API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool(meta={"ui": {"resourceUri": "ui://road-status"}})
def get_road_status(road_ids: str) -> dict:
    """Get current status of major roads in London.

    Args:
        road_ids: Comma-separated road IDs (e.g., 'A2,A40,M25')
    """
    api_key = os.getenv("TFL_API_KEY")

    try:
        params = {}
        if api_key:
            params["app_key"] = api_key

        if not road_ids or not isinstance(road_ids, str):
            return {"error": "Road IDs must be provided as a string"}

        road_list = [r.strip().upper() for r in road_ids.split(",")]
        for road_id in road_list:
            if not road_id or len(road_id) > 10:
                return {"error": f"Invalid road ID format: {road_id}"}

        response = requests.get(
            f"{TFL_API_URL}/Road/{road_ids}",
            params=params,
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Road not found"}

        response.raise_for_status()
        data = response.json()

        roads = []
        for road in data:
            roads.append({
                "id": road.get("id"),
                "display_name": road.get("displayName"),
                "status": road.get("statusSeverity"),
                "status_description": road.get("statusSeverityDescription"),
                "url": road.get("url")
            })

        return {
            "roads": roads,
            "data_source": "Transport for London API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


@mcp.tool
def search_stops(query: str, modes: Optional[str] = None) -> dict:
    """Search for bus stops, tube stations, and other transit stops in London.

    Args:
        query: Search term (station name, postcode, etc.)
        modes: Optional comma-separated transport modes (tube,bus,dlr,overground,elizabeth-line,tram)
    """
    api_key = os.getenv("TFL_API_KEY")

    try:
        params = {"query": query}
        if api_key:
            params["app_key"] = api_key
        if modes:
            params["modes"] = modes

        response = requests.get(
            f"{TFL_API_URL}/StopPoint/Search",
            params=params,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        stops = []
        for match in data.get("matches", [])[:20]:
            stops.append({
                "id": match.get("id"),
                "name": match.get("name"),
                "modes": match.get("modes", []),
                "zone": match.get("zone"),
                "lat": match.get("lat"),
                "lon": match.get("lon")
            })

        return {
            "query": query,
            "total_results": data.get("total", 0),
            "showing": len(stops),
            "stops": stops,
            "data_source": "Transport for London API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
