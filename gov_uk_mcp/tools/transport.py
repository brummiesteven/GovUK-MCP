"""Transport status tool."""
import os
import requests
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error, InputValidator, ValidationError


TFL_API_URL = "https://api.tfl.gov.uk"


def get_tube_status():
    """Get status of all London Underground lines."""
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


def get_line_status(line_id):
    """Get status for a specific line."""
    try:
        # Validate line_id to prevent injection attacks
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


def get_station_arrivals(station_id):
    """Get arrival predictions for a station."""
    try:
        # Validate station_id to prevent injection attacks
        station_id = InputValidator.validate_alphanumeric_id(station_id, "Station ID", max_length=20)
    except ValidationError as e:
        return {"error": str(e)}

    api_key = os.getenv("TFL_API_KEY")

    try:
        params = {}
        if api_key:
            params["app_key"] = api_key

        response = requests.get(
            f"{TFL_API_URL}/StopPoint/{station_id}/Arrivals",
            params=params,
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Station not found"}

        response.raise_for_status()
        data = response.json()

        arrivals = []
        for arrival in data[:10]:  # Limit to 10 arrivals
            arrivals.append({
                "line": arrival.get("lineName"),
                "destination": arrival.get("destinationName"),
                "platform": arrival.get("platformName"),
                "expected_arrival": arrival.get("expectedArrival"),
                "time_to_station": arrival.get("timeToStation"),
                "current_location": arrival.get("currentLocation")
            })

        # Sort by time to station
        arrivals.sort(key=lambda x: x.get("time_to_station", 999999))

        return {
            "station_id": station_id,
            "arrivals": arrivals,
            "data_source": "Transport for London API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


def plan_journey(from_location, to_location, via=None, time=None, time_is_arrival=False):
    """Plan a journey between two locations in London.

    Args:
        from_location: Starting point (postcode, station name, or coordinates)
        to_location: Destination (postcode, station name, or coordinates)
        via: Optional intermediate stop
        time: Optional time for journey (ISO format or HH:MM)
        time_is_arrival: If True, time is arrival time; if False, departure time
    """
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
        for journey in data.get("journeys", [])[:5]:  # Limit to 5 options
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


def get_bike_points(lat=None, lon=None, radius=500):
    """Get bike sharing points (Santander Cycles) near a location.

    Args:
        lat: Latitude (optional, searches all if not provided)
        lon: Longitude (required if lat provided)
        radius: Search radius in meters (default: 500)
    """
    api_key = os.getenv("TFL_API_KEY")

    try:
        params = {}
        if api_key:
            params["app_key"] = api_key

        # If coordinates provided, search nearby
        if lat is not None and lon is not None:
            response = requests.get(
                f"{TFL_API_URL}/BikePoint",
                params={**params, "lat": lat, "lon": lon, "radius": radius},
                timeout=10
            )
        else:
            # Get all bike points
            response = requests.get(
                f"{TFL_API_URL}/BikePoint",
                params=params,
                timeout=10
            )

        response.raise_for_status()
        data = response.json()

        # Limit to 20 results
        bike_points = []
        for point in data[:20]:
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
            "total_results": len(data),
            "showing": len(bike_points),
            "bike_points": bike_points,
            "data_source": "Transport for London API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


def get_road_status(road_ids):
    """Get status of major roads (A roads) in London.

    Args:
        road_ids: Comma-separated road IDs (e.g., "A2,A40,M25")
    """
    api_key = os.getenv("TFL_API_KEY")

    try:
        params = {}
        if api_key:
            params["app_key"] = api_key

        # Validate road_ids format
        if not road_ids or not isinstance(road_ids, str):
            return {"error": "Road IDs must be provided as a string"}

        # Clean and validate road IDs
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


def search_stops(query, modes=None):
    """Search for bus stops, tube stations, and other transit stops.

    Args:
        query: Search term (station name, postcode, etc.)
        modes: Optional comma-separated list of modes (tube,bus,dlr,etc.)
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
        for match in data.get("matches", [])[:20]:  # Limit to 20
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
