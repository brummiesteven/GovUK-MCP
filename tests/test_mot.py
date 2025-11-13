"""Tests for MOT history check tool.

This module tests the check_mot function with mocked API responses,
covering both success and error cases.
"""

from typing import Any, Dict
from unittest.mock import Mock, patch
import pytest
import requests
from gov_uk_mcp.tools.mot import check_mot


class TestCheckMOT:
    """Test MOT history check functionality."""

    def test_check_mot_success(
        self, mock_env_vars: Dict[str, str], sample_mot_response: Dict[str, Any]
    ):
        """Test successful MOT check with valid registration."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_mot_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = check_mot("AB12 CDE")

            # Verify API was called correctly
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args.kwargs
            assert call_kwargs["params"]["registration"] == "AB12CDE"
            assert call_kwargs["headers"]["x-api-key"] == mock_env_vars["DVLA_MOT_API_KEY"]
            assert call_kwargs["timeout"] == 10

            # Verify result structure
            assert result["registration"] == "AB12CDE"
            assert result["make"] == "FORD"
            assert result["model"] == "FOCUS"
            assert result["colour"] == "Blue"
            assert result["fuel_type"] == "Petrol"
            assert result["year"] == "2015"
            assert result["mot_status"] == "PASSED"
            assert result["expiry_date"] == "2025-01-14"
            assert result["test_date"] == "2024-01-15"
            assert result["odometer"] == "45000"
            assert result["odometer_unit"] == "mi"
            assert "advisories" in result
            assert len(result["advisories"]) == 1
            assert result["advisories"][0]["type"] == "ADVISORY"
            assert result["test_history_count"] == 1
            assert result["data_source"] == "DVLA MOT History API"
            assert "retrieved_at" in result

    def test_check_mot_no_api_key(self, monkeypatch: pytest.MonkeyPatch):
        """Test MOT check without API key returns error."""
        # Remove API key from environment
        monkeypatch.delenv("DVLA_MOT_API_KEY", raising=False)

        result = check_mot("AB12CDE")

        assert "error" in result
        assert result["error"] == "MOT API key not configured"

    def test_check_mot_invalid_registration(self, mock_env_vars: Dict[str, str]):
        """Test MOT check with invalid registration format."""
        result = check_mot("INVALID_REG")

        assert "error" in result
        assert "Invalid UK registration format" in result["error"]

    def test_check_mot_empty_registration(self, mock_env_vars: Dict[str, str]):
        """Test MOT check with empty registration."""
        result = check_mot("")

        assert "error" in result
        assert "Registration number is required" in result["error"]

    def test_check_mot_vehicle_not_found(self, mock_env_vars: Dict[str, str]):
        """Test MOT check when vehicle is not found (404 response)."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            result = check_mot("AB12CDE")

            assert "error" in result
            assert result["error"] == "Vehicle not found"

    def test_check_mot_no_mot_data(self, mock_env_vars: Dict[str, str]):
        """Test MOT check when API returns empty data."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = check_mot("AB12CDE")

            assert "error" in result
            assert result["error"] == "No MOT data available"

    def test_check_mot_no_tests_found(self, mock_env_vars: Dict[str, str]):
        """Test MOT check when vehicle has no MOT tests."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {
                    "registration": "AB12CDE",
                    "make": "FORD",
                    "model": "FOCUS",
                    "motTests": [],
                }
            ]
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = check_mot("AB12CDE")

            assert result["registration"] == "AB12CDE"
            assert result["make"] == "FORD"
            assert result["model"] == "FOCUS"
            assert result["status"] == "No MOT tests found"

    def test_check_mot_with_multiple_tests(self, mock_env_vars: Dict[str, str]):
        """Test MOT check returns most recent test from multiple tests."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
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
                            "odometerValue": "50000",
                            "odometerUnit": "mi",
                            "rfrAndComments": [],
                        },
                        {
                            "completedDate": "2023-01-10",
                            "testResult": "PASSED",
                            "expiryDate": "2024-01-09",
                            "odometerValue": "45000",
                            "odometerUnit": "mi",
                            "rfrAndComments": [],
                        },
                    ],
                }
            ]
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = check_mot("AB12CDE")

            # Should return the most recent test (first in array)
            assert result["test_date"] == "2024-01-15"
            assert result["expiry_date"] == "2025-01-14"
            assert result["odometer"] == "50000"
            assert result["test_history_count"] == 2

    def test_check_mot_timeout_error(self, mock_env_vars: Dict[str, str]):
        """Test MOT check handles timeout error."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timeout")

            result = check_mot("AB12CDE")

            assert "error" in result
            assert result["error"] == "Service temporarily unavailable. Please try again."

    def test_check_mot_network_error(self, mock_env_vars: Dict[str, str]):
        """Test MOT check handles network error."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")

            result = check_mot("AB12CDE")

            assert "error" in result
            assert result["error"] == "Network error. Please check your connection and try again."

    def test_check_mot_http_error_500(self, mock_env_vars: Dict[str, str]):
        """Test MOT check handles HTTP 500 error."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500

            def raise_for_status():
                raise requests.HTTPError(response=mock_response)

            mock_response.raise_for_status = raise_for_status
            mock_get.return_value = mock_response

            result = check_mot("AB12CDE")

            assert "error" in result
            assert result["error"] == "External service error. Please try again later."

    def test_check_mot_http_error_401(self, mock_env_vars: Dict[str, str]):
        """Test MOT check handles HTTP 401 authentication error."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401

            def raise_for_status():
                raise requests.HTTPError(response=mock_response)

            mock_response.raise_for_status = raise_for_status
            mock_get.return_value = mock_response

            result = check_mot("AB12CDE")

            assert "error" in result
            assert result["error"] == "Authentication error. Please check configuration."

    def test_check_mot_http_error_429(self, mock_env_vars: Dict[str, str]):
        """Test MOT check handles HTTP 429 rate limit error."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 429

            def raise_for_status():
                raise requests.HTTPError(response=mock_response)

            mock_response.raise_for_status = raise_for_status
            mock_get.return_value = mock_response

            result = check_mot("AB12CDE")

            assert "error" in result
            assert result["error"] == "Rate limit exceeded. Please try again later."

    def test_check_mot_registration_normalization(self, mock_env_vars: Dict[str, str]):
        """Test that registration is properly normalized (uppercase, no spaces)."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {
                    "registration": "AB12CDE",
                    "make": "FORD",
                    "model": "FOCUS",
                    "motTests": [
                        {
                            "completedDate": "2024-01-15",
                            "testResult": "PASSED",
                            "expiryDate": "2025-01-14",
                            "odometerValue": "45000",
                            "odometerUnit": "mi",
                            "rfrAndComments": [],
                        }
                    ],
                }
            ]
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Test with lowercase and spaces
            result = check_mot("ab12 cde")

            # Verify API was called with normalized registration
            call_kwargs = mock_get.call_args.kwargs
            assert call_kwargs["params"]["registration"] == "AB12CDE"

            assert "error" not in result
            assert result["registration"] == "AB12CDE"

    def test_check_mot_without_advisories(self, mock_env_vars: Dict[str, str]):
        """Test MOT check when there are no advisories."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
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
                            "rfrAndComments": [],
                        }
                    ],
                }
            ]
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = check_mot("AB12CDE")

            assert "advisories" not in result or len(result.get("advisories", [])) == 0

    def test_check_mot_failed_test(self, mock_env_vars: Dict[str, str]):
        """Test MOT check with failed MOT test."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
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
                            "testResult": "FAILED",
                            "expiryDate": None,
                            "odometerValue": "45000",
                            "odometerUnit": "mi",
                            "rfrAndComments": [
                                {"type": "FAIL", "text": "Brake disc excessively worn"}
                            ],
                        }
                    ],
                }
            ]
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = check_mot("AB12CDE")

            assert result["mot_status"] == "FAILED"
            assert result["expiry_date"] is None
            assert len(result["advisories"]) == 1
            assert result["advisories"][0]["type"] == "FAIL"
