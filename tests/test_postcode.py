"""Tests for postcode lookup tool.

This module tests the postcode lookup functions with mocked API responses,
covering both success and error cases.
"""

from typing import Any, Dict
from unittest.mock import Mock, patch
import pytest
import requests
from gov_uk_mcp.tools.postcode import lookup_postcode, nearest_postcodes


class TestLookupPostcode:
    """Test postcode lookup functionality."""

    def test_lookup_postcode_success(self, sample_postcode_response: Dict[str, Any]):
        """Test successful postcode lookup with valid postcode."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_postcode_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = lookup_postcode("SW1A 1AA")

            # Verify API was called correctly
            mock_get.assert_called_once()
            assert "postcodes/SW1A1AA" in mock_get.call_args.args[0]
            assert mock_get.call_args.kwargs["timeout"] == 10

            # Verify result structure
            assert result["postcode"] == "SW1A 1AA"
            assert result["latitude"] == 51.5014
            assert result["longitude"] == -0.1419
            assert result["admin_district"] == "Westminster"
            assert result["parliamentary_constituency"] == "Cities of London and Westminster"
            assert result["region"] == "London"
            assert result["country"] == "England"
            assert result["ward"] == "St James's"
            assert "codes" in result
            assert result["codes"]["admin_district"] == "E09000033"
            assert result["data_source"] == "Postcodes.io API"
            assert "retrieved_at" in result

    def test_lookup_postcode_invalid_format(self):
        """Test postcode lookup with invalid postcode format."""
        result = lookup_postcode("INVALID")

        assert "error" in result
        assert "Invalid UK postcode format" in result["error"]

    def test_lookup_postcode_empty(self):
        """Test postcode lookup with empty postcode."""
        result = lookup_postcode("")

        assert "error" in result
        assert "Postcode is required" in result["error"]

    def test_lookup_postcode_not_found(self):
        """Test postcode lookup when postcode is not found (404 response)."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            result = lookup_postcode("SW1A 1AA")

            assert "error" in result
            assert result["error"] == "Postcode not found"

    def test_lookup_postcode_invalid_response_status(self):
        """Test postcode lookup when API returns non-200 status in response."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": 404, "error": "Invalid postcode"}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = lookup_postcode("SW1A 1AA")

            assert "error" in result
            assert result["error"] == "Invalid postcode"

    def test_lookup_postcode_timeout_error(self):
        """Test postcode lookup handles timeout error."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timeout")

            result = lookup_postcode("SW1A 1AA")

            assert "error" in result
            assert result["error"] == "Service temporarily unavailable. Please try again."

    def test_lookup_postcode_network_error(self):
        """Test postcode lookup handles network error."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")

            result = lookup_postcode("SW1A 1AA")

            assert "error" in result
            assert result["error"] == "Network error. Please check your connection and try again."

    def test_lookup_postcode_http_error_500(self):
        """Test postcode lookup handles HTTP 500 error."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500

            def raise_for_status():
                raise requests.HTTPError(response=mock_response)

            mock_response.raise_for_status = raise_for_status
            mock_get.return_value = mock_response

            result = lookup_postcode("SW1A 1AA")

            assert "error" in result
            assert result["error"] == "External service error. Please try again later."

    def test_lookup_postcode_normalization(self, sample_postcode_response: Dict[str, Any]):
        """Test that postcode is properly normalized (uppercase, trimmed)."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_postcode_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Test with lowercase and extra spaces
            result = lookup_postcode("  sw1a 1aa  ")

            # Verify API was called with normalized postcode
            assert "postcodes/SW1A1AA" in mock_get.call_args.args[0]

            assert "error" not in result
            assert result["postcode"] == "SW1A 1AA"

    def test_lookup_postcode_with_missing_optional_fields(self):
        """Test postcode lookup with missing optional fields in response."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": 200,
                "result": {
                    "postcode": "SW1A 1AA",
                    "latitude": 51.5014,
                    "longitude": -0.1419,
                    "admin_district": "Westminster",
                    "codes": {},
                },
            }
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = lookup_postcode("SW1A 1AA")

            assert result["postcode"] == "SW1A 1AA"
            assert result["latitude"] == 51.5014
            assert result["longitude"] == -0.1419
            # Missing fields should be None
            assert result.get("parliamentary_constituency") is None
            assert result.get("region") is None


class TestNearestPostcodes:
    """Test nearest postcodes functionality."""

    def test_nearest_postcodes_success(self):
        """Test successful nearest postcodes lookup."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": 200,
                "result": [
                    {
                        "postcode": "SW1A 1AB",
                        "distance": 23.5,
                        "latitude": 51.5015,
                        "longitude": -0.1420,
                        "admin_district": "Westminster",
                    },
                    {
                        "postcode": "SW1A 1AC",
                        "distance": 45.2,
                        "latitude": 51.5016,
                        "longitude": -0.1421,
                        "admin_district": "Westminster",
                    },
                ],
            }
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = nearest_postcodes("SW1A 1AA", limit=10)

            # Verify API was called correctly
            mock_get.assert_called_once()
            assert "postcodes/SW1A1AA/nearest" in mock_get.call_args.args[0]
            assert mock_get.call_args.kwargs["params"]["limit"] == 10
            assert mock_get.call_args.kwargs["timeout"] == 10

            # Verify result structure
            assert result["search_postcode"] == "SW1A1AA"
            assert "nearest_postcodes" in result
            assert len(result["nearest_postcodes"]) == 2
            assert result["nearest_postcodes"][0]["postcode"] == "SW1A 1AB"
            assert result["nearest_postcodes"][0]["distance"] == 23.5
            assert result["nearest_postcodes"][1]["postcode"] == "SW1A 1AC"
            assert result["nearest_postcodes"][1]["distance"] == 45.2
            assert result["data_source"] == "Postcodes.io API"
            assert "retrieved_at" in result

    def test_nearest_postcodes_default_limit(self):
        """Test nearest postcodes with default limit parameter."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": 200, "result": []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = nearest_postcodes("SW1A 1AA")

            # Verify default limit is 10
            assert mock_get.call_args.kwargs["params"]["limit"] == 10
            assert "error" not in result

    def test_nearest_postcodes_custom_limit(self):
        """Test nearest postcodes with custom limit parameter."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": 200, "result": []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = nearest_postcodes("SW1A 1AA", limit=5)

            # Verify custom limit is used
            assert mock_get.call_args.kwargs["params"]["limit"] == 5
            assert "error" not in result

    def test_nearest_postcodes_invalid_postcode(self):
        """Test nearest postcodes with invalid postcode format."""
        result = nearest_postcodes("INVALID")

        assert "error" in result
        assert "Invalid UK postcode format" in result["error"]

    def test_nearest_postcodes_empty_postcode(self):
        """Test nearest postcodes with empty postcode."""
        result = nearest_postcodes("")

        assert "error" in result
        assert "Postcode is required" in result["error"]

    def test_nearest_postcodes_not_found(self):
        """Test nearest postcodes when postcode is not found (404 response)."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            result = nearest_postcodes("SW1A 1AA")

            assert "error" in result
            assert result["error"] == "Postcode not found"

    def test_nearest_postcodes_invalid_response_status(self):
        """Test nearest postcodes when API returns non-200 status in response."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": 404, "error": "Invalid postcode"}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = nearest_postcodes("SW1A 1AA")

            assert "error" in result
            assert result["error"] == "Invalid postcode"

    def test_nearest_postcodes_timeout_error(self):
        """Test nearest postcodes handles timeout error."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timeout")

            result = nearest_postcodes("SW1A 1AA")

            assert "error" in result
            assert result["error"] == "Service temporarily unavailable. Please try again."

    def test_nearest_postcodes_network_error(self):
        """Test nearest postcodes handles network error."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")

            result = nearest_postcodes("SW1A 1AA")

            assert "error" in result
            assert result["error"] == "Network error. Please check your connection and try again."

    def test_nearest_postcodes_empty_results(self):
        """Test nearest postcodes when API returns no results."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": 200, "result": []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = nearest_postcodes("SW1A 1AA")

            assert "error" not in result
            assert result["nearest_postcodes"] == []

    def test_nearest_postcodes_normalization(self):
        """Test that postcode is properly normalized in nearest postcodes search."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": 200, "result": []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Test with lowercase and extra spaces
            result = nearest_postcodes("  sw1a 1aa  ")

            # Verify API was called with normalized postcode
            assert "postcodes/SW1A1AA/nearest" in mock_get.call_args.args[0]

            assert "error" not in result
            assert result["search_postcode"] == "SW1A1AA"
