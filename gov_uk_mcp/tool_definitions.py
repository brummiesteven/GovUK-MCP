"""Tool definitions and registrations for Gov.uk MCP Server."""
from gov_uk_mcp.registry import ToolRegistry

# Import all tool functions
from gov_uk_mcp.tools.companies_house import (
    search_companies,
    get_company,
    get_company_officers,
    get_company_filing_history
)
from gov_uk_mcp.tools.postcode import lookup_postcode, nearest_postcodes
from gov_uk_mcp.tools.food_hygiene import search_food_establishments
from gov_uk_mcp.tools.bank_holidays import get_bank_holidays
from gov_uk_mcp.tools.search import search_govuk
from gov_uk_mcp.tools.flood_warnings import get_flood_warnings
from gov_uk_mcp.tools.police_crime import get_crime_by_postcode
from gov_uk_mcp.tools.epc import search_epc_by_postcode
from gov_uk_mcp.tools.courts import find_courts
from gov_uk_mcp.tools.charity import search_charities, get_charity
from gov_uk_mcp.tools.nhs import find_gp_surgeries, find_hospitals, find_pharmacies
from gov_uk_mcp.tools.transport import (
    get_tube_status,
    get_line_status,
    plan_journey,
    get_bike_points,
    get_road_status,
    search_stops
)
from gov_uk_mcp.tools.legislation import search_legislation
from gov_uk_mcp.tools.cqc import search_cqc_providers, get_cqc_provider
from gov_uk_mcp.tools.mps import find_mp
from gov_uk_mcp.tools.hansard import search_hansard
from gov_uk_mcp.tools.voting import get_voting_record, search_divisions
from gov_uk_mcp.tools.parliamentary_questions import search_questions, get_questions_by_mp


# Register all tools
ToolRegistry.register(
    name="search_companies",
    description="Search for UK companies by name using Companies House API.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Company name to search for"
            },
            "items_per_page": {
                "type": "integer",
                "description": "Number of results to return (default: 20)",
                "default": 20
            }
        },
        "required": ["query"]
    }
)(search_companies)

ToolRegistry.register(
    name="get_company",
    description="Get detailed company information by company number from Companies House.",
    input_schema={
        "type": "object",
        "properties": {
            "company_number": {
                "type": "string",
                "description": "Company number (e.g., 12345678)"
            }
        },
        "required": ["company_number"]
    }
)(get_company)

ToolRegistry.register(
    name="get_company_officers",
    description="Get list of company officers (directors, secretaries) by company number.",
    input_schema={
        "type": "object",
        "properties": {
            "company_number": {
                "type": "string",
                "description": "Company number (e.g., 12345678)"
            }
        },
        "required": ["company_number"]
    }
)(get_company_officers)

ToolRegistry.register(
    name="get_company_filing_history",
    description="Get company filing history by company number from Companies House.",
    input_schema={
        "type": "object",
        "properties": {
            "company_number": {
                "type": "string",
                "description": "Company number (e.g., 12345678)"
            },
            "items_per_page": {
                "type": "integer",
                "description": "Number of results to return (default: 20)",
                "default": 20
            }
        },
        "required": ["company_number"]
    }
)(get_company_filing_history)

ToolRegistry.register(
    name="lookup_postcode",
    description="Look up UK postcode details including location, council, constituency, and coordinates.",
    input_schema={
        "type": "object",
        "properties": {
            "postcode": {
                "type": "string",
                "description": "UK postcode (e.g., SW1A 1AA)"
            }
        },
        "required": ["postcode"]
    }
)(lookup_postcode)

ToolRegistry.register(
    name="nearest_postcodes",
    description="Find nearest postcodes to a given UK postcode.",
    input_schema={
        "type": "object",
        "properties": {
            "postcode": {
                "type": "string",
                "description": "UK postcode (e.g., SW1A 1AA)"
            },
            "limit": {
                "type": "integer",
                "description": "Number of nearest postcodes to return (default: 10)",
                "default": 10
            }
        },
        "required": ["postcode"]
    }
)(nearest_postcodes)

ToolRegistry.register(
    name="search_food_establishments",
    description="Search for food establishments and their hygiene ratings by name, postcode, or local authority.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Business name to search for"
            },
            "postcode": {
                "type": "string",
                "description": "Postcode to search in"
            },
            "local_authority": {
                "type": "string",
                "description": "Local authority ID"
            }
        }
    }
)(search_food_establishments)

ToolRegistry.register(
    name="get_bank_holidays",
    description="Get UK bank holidays. Can filter by country (england-and-wales, scotland, northern-ireland).",
    input_schema={
        "type": "object",
        "properties": {
            "country": {
                "type": "string",
                "description": "Country to get holidays for (optional)",
                "enum": ["england-and-wales", "scotland", "northern-ireland"]
            }
        }
    }
)(get_bank_holidays)

ToolRegistry.register(
    name="search_govuk",
    description="Search gov.uk content for guidance, policy documents, and other government information.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "count": {
                "type": "integer",
                "description": "Number of results to return (default: 10)",
                "default": 10
            }
        },
        "required": ["query"]
    }
)(search_govuk)

ToolRegistry.register(
    name="get_flood_warnings",
    description="Get active flood warnings for England. Can filter by postcode or area.",
    input_schema={
        "type": "object",
        "properties": {
            "postcode": {
                "type": "string",
                "description": "Postcode to search for (optional)"
            },
            "area": {
                "type": "string",
                "description": "Area name to search for (optional)"
            }
        }
    }
)(get_flood_warnings)

ToolRegistry.register(
    name="get_crime_by_postcode",
    description="Get street-level crime data for a postcode area.",
    input_schema={
        "type": "object",
        "properties": {
            "postcode": {
                "type": "string",
                "description": "UK postcode"
            }
        },
        "required": ["postcode"]
    }
)(get_crime_by_postcode)

ToolRegistry.register(
    name="search_epc_by_postcode",
    description="Search for Energy Performance Certificates by postcode. Returns energy ratings (A-G) and property details.",
    input_schema={
        "type": "object",
        "properties": {
            "postcode": {
                "type": "string",
                "description": "UK postcode"
            }
        },
        "required": ["postcode"]
    }
)(search_epc_by_postcode)

ToolRegistry.register(
    name="find_courts",
    description="Find courts by postcode or name. Returns court details, types, and contact information.",
    input_schema={
        "type": "object",
        "properties": {
            "postcode": {
                "type": "string",
                "description": "UK postcode"
            },
            "name": {
                "type": "string",
                "description": "Court name to search for"
            }
        }
    }
)(find_courts)

ToolRegistry.register(
    name="search_charities",
    description="Search for registered charities by name.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Charity name to search for"
            }
        },
        "required": ["name"]
    }
)(search_charities)

ToolRegistry.register(
    name="get_charity",
    description="Get detailed charity information by registration number.",
    input_schema={
        "type": "object",
        "properties": {
            "charity_number": {
                "type": "string",
                "description": "Charity registration number"
            }
        },
        "required": ["charity_number"]
    }
)(get_charity)

ToolRegistry.register(
    name="find_gp_surgeries",
    description="Find GP surgeries near a postcode.",
    input_schema={
        "type": "object",
        "properties": {
            "postcode": {
                "type": "string",
                "description": "UK postcode"
            }
        },
        "required": ["postcode"]
    }
)(find_gp_surgeries)

ToolRegistry.register(
    name="find_hospitals",
    description="Find hospitals near a postcode.",
    input_schema={
        "type": "object",
        "properties": {
            "postcode": {
                "type": "string",
                "description": "UK postcode"
            }
        },
        "required": ["postcode"]
    }
)(find_hospitals)

ToolRegistry.register(
    name="find_pharmacies",
    description="Find pharmacies near a postcode.",
    input_schema={
        "type": "object",
        "properties": {
            "postcode": {
                "type": "string",
                "description": "UK postcode"
            }
        },
        "required": ["postcode"]
    }
)(find_pharmacies)

ToolRegistry.register(
    name="get_tube_status",
    description="Get current status of all London Underground lines.",
    input_schema={
        "type": "object",
        "properties": {}
    }
)(get_tube_status)

ToolRegistry.register(
    name="get_line_status",
    description="Get status for a specific London Underground line.",
    input_schema={
        "type": "object",
        "properties": {
            "line_id": {
                "type": "string",
                "description": "Line ID (e.g., 'central', 'northern', 'piccadilly')"
            }
        },
        "required": ["line_id"]
    }
)(get_line_status)

ToolRegistry.register(
    name="plan_journey",
    description="Plan a journey between two locations in London using public transport. Returns multiple journey options with step-by-step directions.",
    input_schema={
        "type": "object",
        "properties": {
            "from_location": {
                "type": "string",
                "description": "Starting point (postcode, station name, or address)"
            },
            "to_location": {
                "type": "string",
                "description": "Destination (postcode, station name, or address)"
            },
            "via": {
                "type": "string",
                "description": "Optional intermediate stop"
            },
            "time": {
                "type": "string",
                "description": "Optional time for journey (ISO format or HH:MM)"
            },
            "time_is_arrival": {
                "type": "boolean",
                "description": "If true, time is arrival time; if false, departure time (default: false)",
                "default": False
            }
        },
        "required": ["from_location", "to_location"]
    }
)(plan_journey)

ToolRegistry.register(
    name="get_bike_points",
    description="Get Santander Cycles (bike sharing) docking stations in London. Shows bikes available and empty docks.",
    input_schema={
        "type": "object",
        "properties": {
            "lat": {
                "type": "number",
                "description": "Latitude for location search (optional)"
            },
            "lon": {
                "type": "number",
                "description": "Longitude for location search (required if lat provided)"
            },
            "radius": {
                "type": "integer",
                "description": "Search radius in meters (default: 500)",
                "default": 500
            }
        }
    }
)(get_bike_points)

ToolRegistry.register(
    name="get_road_status",
    description="Get current status of major roads in London (A roads, motorways). Shows traffic conditions and closures.",
    input_schema={
        "type": "object",
        "properties": {
            "road_ids": {
                "type": "string",
                "description": "Comma-separated road IDs (e.g., 'A2,A40,M25')"
            }
        },
        "required": ["road_ids"]
    }
)(get_road_status)

ToolRegistry.register(
    name="search_stops",
    description="Search for bus stops, tube stations, DLR stations, and other public transport stops in London.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search term (station name, postcode, area)"
            },
            "modes": {
                "type": "string",
                "description": "Optional comma-separated transport modes (tube,bus,dlr,overground,elizabeth-line,tram)"
            }
        },
        "required": ["query"]
    }
)(search_stops)

ToolRegistry.register(
    name="search_legislation",
    description="Search UK legislation by keyword.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "limit": {
                "type": "integer",
                "description": "Number of results (default: 20)",
                "default": 20
            }
        },
        "required": ["query"]
    }
)(search_legislation)

ToolRegistry.register(
    name="search_cqc_providers",
    description="Search for CQC registered care providers by name or postcode.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Provider name"
            },
            "postcode": {
                "type": "string",
                "description": "UK postcode"
            }
        }
    }
)(search_cqc_providers)

ToolRegistry.register(
    name="get_cqc_provider",
    description="Get detailed CQC ratings and information for a care provider.",
    input_schema={
        "type": "object",
        "properties": {
            "location_id": {
                "type": "string",
                "description": "CQC location ID"
            }
        },
        "required": ["location_id"]
    }
)(get_cqc_provider)

ToolRegistry.register(
    name="find_mp",
    description="Find MP by name, constituency, or postcode. Returns MP details including party and constituency.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "MP name, constituency name, or UK postcode"
            }
        },
        "required": ["query"]
    }
)(find_mp)

ToolRegistry.register(
    name="search_hansard",
    description="Search parliamentary debates in Hansard (2015-present). Returns debate transcripts and speeches.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search term"
            },
            "date_from": {
                "type": "string",
                "description": "Start date (YYYY-MM-DD format, optional)"
            },
            "date_to": {
                "type": "string",
                "description": "End date (YYYY-MM-DD format, optional)"
            },
            "speaker": {
                "type": "string",
                "description": "Filter by speaker name (optional)"
            }
        },
        "required": ["query"]
    }
)(search_hansard)

ToolRegistry.register(
    name="get_voting_record",
    description="Get voting record for an MP. Shows how they voted on specific bills or recent voting history.",
    input_schema={
        "type": "object",
        "properties": {
            "mp_name_or_id": {
                "type": "string",
                "description": "MP name or member ID"
            },
            "division_id": {
                "type": "string",
                "description": "Specific division ID (optional)"
            },
            "limit": {
                "type": "integer",
                "description": "Number of recent votes to return (default: 20)",
                "default": 20
            }
        },
        "required": ["mp_name_or_id"]
    }
)(get_voting_record)

ToolRegistry.register(
    name="search_divisions",
    description="Search parliamentary divisions (votes) by keyword.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search term"
            },
            "limit": {
                "type": "integer",
                "description": "Number of results (default: 20)",
                "default": 20
            }
        },
        "required": ["query"]
    }
)(search_divisions)

ToolRegistry.register(
    name="search_questions",
    description="Search parliamentary written questions and answers.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search term"
            },
            "mp_name": {
                "type": "string",
                "description": "Filter by MP name (optional)"
            },
            "department": {
                "type": "string",
                "description": "Filter by government department (optional)"
            },
            "limit": {
                "type": "integer",
                "description": "Number of results (default: 20)",
                "default": 20
            }
        },
        "required": ["query"]
    }
)(search_questions)

ToolRegistry.register(
    name="get_questions_by_mp",
    description="Get all parliamentary questions asked by a specific MP.",
    input_schema={
        "type": "object",
        "properties": {
            "mp_name": {
                "type": "string",
                "description": "MP name"
            },
            "limit": {
                "type": "integer",
                "description": "Number of results (default: 20)",
                "default": 20
            }
        },
        "required": ["mp_name"]
    }
)(get_questions_by_mp)
