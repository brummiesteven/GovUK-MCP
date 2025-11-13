"""Pytest configuration and shared fixtures for Gov.uk MCP Server tests.

This module provides common test fixtures and configuration used across
all test files.
"""

import os
import sys
from typing import Any, Dict
from unittest.mock import Mock
import pytest
import requests

# Mock mcp module for testing
sys.modules["mcp"] = Mock()
sys.modules["mcp.types"] = Mock()
sys.modules["mcp.server"] = Mock()
sys.modules["mcp.server.stdio"] = Mock()

# Import mock types after setting up mocks
from tests.mock_mcp import Tool

sys.modules["mcp"].types = Mock()
sys.modules["mcp"].types.Tool = Tool


@pytest.fixture
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> Dict[str, str]:
    """Provide mock environment variables for API keys.

    Args:
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        Dictionary of environment variables set
    """
    env_vars = {
        "DVLA_MOT_API_KEY": "test_mot_api_key_12345",
        "COMPANIES_HOUSE_API_KEY": "test_companies_house_key_67890",
        "DVLA_VEHICLE_API_KEY": "test_vehicle_api_key_abcde",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars


@pytest.fixture
def mock_requests_get(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Provide a mock for requests.get.

    Args:
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        Mock object for requests.get
    """
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr("requests.get", mock_get)

    return mock_get


@pytest.fixture
def mock_successful_response() -> Mock:
    """Create a mock successful HTTP response.

    Returns:
        Mock Response object with 200 status code
    """
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": 200, "result": {}}
    mock_response.raise_for_status = Mock()
    return mock_response


@pytest.fixture
def mock_404_response() -> Mock:
    """Create a mock 404 HTTP response.

    Returns:
        Mock Response object with 404 status code
    """
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": "Not found"}

    def raise_for_status():
        raise requests.HTTPError(response=mock_response)

    mock_response.raise_for_status = raise_for_status
    return mock_response


@pytest.fixture
def mock_timeout_error() -> requests.Timeout:
    """Create a mock timeout error.

    Returns:
        requests.Timeout exception
    """
    return requests.Timeout("Connection timeout")


@pytest.fixture
def mock_network_error() -> requests.RequestException:
    """Create a mock network error.

    Returns:
        requests.RequestException
    """
    return requests.RequestException("Network error")


@pytest.fixture
def sample_mot_response() -> Dict[str, Any]:
    """Provide sample MOT API response data.

    Returns:
        Dictionary containing sample MOT data
    """
    return [
        {
            "registration": "AB12CDE",
            "make": "FORD",
            "model": "FOCUS",
            "primaryColour": "Blue",
            "fuelType": "Petrol",
            "manufactureYear": "2015",
            "motTests": [
                {
                    "completedDate": "2024-01-15",
                    "testResult": "PASSED",
                    "expiryDate": "2025-01-14",
                    "odometerValue": "45000",
                    "odometerUnit": "mi",
                    "rfrAndComments": [
                        {"type": "ADVISORY", "text": "Brake pad wear"}
                    ],
                }
            ],
        }
    ]


@pytest.fixture
def sample_postcode_response() -> Dict[str, Any]:
    """Provide sample Postcodes.io API response data.

    Returns:
        Dictionary containing sample postcode data
    """
    return {
        "status": 200,
        "result": {
            "postcode": "SW1A 1AA",
            "latitude": 51.5014,
            "longitude": -0.1419,
            "admin_district": "Westminster",
            "parliamentary_constituency": "Cities of London and Westminster",
            "region": "London",
            "country": "England",
            "european_electoral_region": "London",
            "primary_care_trust": "Westminster",
            "admin_ward": "St James's",
            "parish": None,
            "codes": {
                "admin_district": "E09000033",
                "admin_county": "E99999999",
                "admin_ward": "E05013806",
                "parish": "E43000236",
                "parliamentary_constituency": "E14000639",
                "ccg": "E38000031",
            },
        },
    }


@pytest.fixture
def sample_companies_search_response() -> Dict[str, Any]:
    """Provide sample Companies House search API response data.

    Returns:
        Dictionary containing sample company search results
    """
    return {
        "total_results": 2,
        "items": [
            {
                "company_number": "12345678",
                "title": "TEST COMPANY LTD",
                "company_status": "active",
                "company_type": "ltd",
                "date_of_creation": "2020-01-15",
                "address": {
                    "premises": "1",
                    "address_line_1": "Test Street",
                    "locality": "London",
                    "postal_code": "SW1A 1AA",
                },
            },
            {
                "company_number": "87654321",
                "title": "ANOTHER TEST COMPANY LTD",
                "company_status": "active",
                "company_type": "ltd",
                "date_of_creation": "2019-06-20",
                "address": {
                    "premises": "2",
                    "address_line_1": "Example Road",
                    "locality": "Manchester",
                    "postal_code": "M1 1AA",
                },
            },
        ],
    }


@pytest.fixture
def sample_company_details_response() -> Dict[str, Any]:
    """Provide sample Companies House company details API response data.

    Returns:
        Dictionary containing sample company details
    """
    return {
        "company_number": "12345678",
        "company_name": "TEST COMPANY LTD",
        "company_status": "active",
        "company_type": "ltd",
        "date_of_creation": "2020-01-15",
        "jurisdiction": "england-wales",
        "registered_office_address": {
            "address_line_1": "1 Test Street",
            "locality": "London",
            "postal_code": "SW1A 1AA",
            "country": "England",
        },
        "sic_codes": ["62012"],
        "accounts": {
            "next_due": "2025-10-31",
            "overdue": False,
        },
        "confirmation_statement": {
            "next_due": "2025-01-28",
            "overdue": False,
        },
        "has_insolvency_history": False,
        "has_charges": False,
    }


@pytest.fixture(autouse=True)
def reset_tool_registry():
    """Reset ToolRegistry before each test to ensure clean state.

    This fixture runs automatically before each test to prevent
    test pollution from registered tools.
    """
    from gov_uk_mcp.registry import ToolRegistry

    # Store original tools
    original_tools = ToolRegistry._tools.copy()

    yield

    # Restore original tools after test
    ToolRegistry._tools = original_tools
