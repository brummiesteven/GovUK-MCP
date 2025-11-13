"""Tests for Companies House lookup tools.

This module tests the Companies House functions with mocked API responses,
covering search, company details, officers, and filing history.
"""

from typing import Any, Dict
from unittest.mock import Mock, patch
import pytest
import requests
from gov_uk_mcp.tools.companies_house import (
    search_companies,
    get_company,
    get_company_officers,
    get_company_filing_history,
)


class TestSearchCompanies:
    """Test company search functionality."""

    def test_search_companies_success(
        self,
        mock_env_vars: Dict[str, str],
        sample_companies_search_response: Dict[str, Any],
    ):
        """Test successful company search."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_companies_search_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = search_companies("TEST COMPANY", items_per_page=20)

            # Verify API was called correctly
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args.kwargs
            assert call_kwargs["params"]["q"] == "TEST COMPANY"
            assert call_kwargs["params"]["items_per_page"] == 20
            assert call_kwargs["auth"] == (mock_env_vars["COMPANIES_HOUSE_API_KEY"], "")
            assert call_kwargs["timeout"] == 10

            # Verify result structure
            assert result["total_results"] == 2
            assert len(result["companies"]) == 2
            assert result["companies"][0]["company_number"] == "12345678"
            assert result["companies"][0]["title"] == "TEST COMPANY LTD"
            assert result["companies"][0]["company_status"] == "active"
            assert result["companies"][1]["company_number"] == "87654321"
            assert result["data_source"] == "Companies House API"
            assert "retrieved_at" in result

    def test_search_companies_no_api_key(self, monkeypatch: pytest.MonkeyPatch):
        """Test company search without API key returns error."""
        monkeypatch.delenv("COMPANIES_HOUSE_API_KEY", raising=False)

        result = search_companies("TEST COMPANY")

        assert "error" in result
        assert result["error"] == "Companies House API key not configured"

    def test_search_companies_default_items_per_page(self, mock_env_vars: Dict[str, str]):
        """Test company search with default items_per_page parameter."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"items": []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = search_companies("TEST")

            # Verify default items_per_page is 20
            assert mock_get.call_args.kwargs["params"]["items_per_page"] == 20

    def test_search_companies_custom_items_per_page(self, mock_env_vars: Dict[str, str]):
        """Test company search with custom items_per_page parameter."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"items": []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = search_companies("TEST", items_per_page=50)

            # Verify custom items_per_page is used
            assert mock_get.call_args.kwargs["params"]["items_per_page"] == 50

    def test_search_companies_empty_results(self, mock_env_vars: Dict[str, str]):
        """Test company search with no results."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"total_results": 0, "items": []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = search_companies("NONEXISTENT")

            assert result["total_results"] == 0
            assert result["companies"] == []

    def test_search_companies_timeout_error(self, mock_env_vars: Dict[str, str]):
        """Test company search handles timeout error."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timeout")

            result = search_companies("TEST")

            assert "error" in result
            assert result["error"] == "Service temporarily unavailable. Please try again."

    def test_search_companies_network_error(self, mock_env_vars: Dict[str, str]):
        """Test company search handles network error."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")

            result = search_companies("TEST")

            assert "error" in result
            assert result["error"] == "Network error. Please check your connection and try again."

    def test_search_companies_http_error_429(self, mock_env_vars: Dict[str, str]):
        """Test company search handles HTTP 429 rate limit error."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 429

            def raise_for_status():
                raise requests.HTTPError(response=mock_response)

            mock_response.raise_for_status = raise_for_status
            mock_get.return_value = mock_response

            result = search_companies("TEST")

            assert "error" in result
            assert result["error"] == "Rate limit exceeded. Please try again later."


class TestGetCompany:
    """Test get company details functionality."""

    def test_get_company_success(
        self,
        mock_env_vars: Dict[str, str],
        sample_company_details_response: Dict[str, Any],
    ):
        """Test successful company details retrieval."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_company_details_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = get_company("12345678")

            # Verify API was called correctly
            mock_get.assert_called_once()
            assert "company/12345678" in mock_get.call_args.args[0]
            assert mock_get.call_args.kwargs["auth"] == (
                mock_env_vars["COMPANIES_HOUSE_API_KEY"],
                "",
            )

            # Verify result structure
            assert result["company_number"] == "12345678"
            assert result["company_name"] == "TEST COMPANY LTD"
            assert result["company_status"] == "active"
            assert result["company_type"] == "ltd"
            assert result["date_of_creation"] == "2020-01-15"
            assert result["has_insolvency_history"] is False
            assert result["has_charges"] is False
            assert result["data_source"] == "Companies House API"
            assert "retrieved_at" in result

    def test_get_company_no_api_key(self, monkeypatch: pytest.MonkeyPatch):
        """Test get company without API key returns error."""
        monkeypatch.delenv("COMPANIES_HOUSE_API_KEY", raising=False)

        result = get_company("12345678")

        assert "error" in result
        assert result["error"] == "Companies House API key not configured"

    def test_get_company_invalid_number(self, mock_env_vars: Dict[str, str]):
        """Test get company with invalid company number format."""
        result = get_company("INVALID")

        assert "error" in result
        assert "Invalid company number format" in result["error"]

    def test_get_company_empty_number(self, mock_env_vars: Dict[str, str]):
        """Test get company with empty company number."""
        result = get_company("")

        assert "error" in result
        assert "Company number is required" in result["error"]

    def test_get_company_not_found(self, mock_env_vars: Dict[str, str]):
        """Test get company when company is not found (404 response)."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            result = get_company("12345678")

            assert "error" in result
            assert result["error"] == "Company not found"

    def test_get_company_number_padding(self, mock_env_vars: Dict[str, str]):
        """Test get company with short company number gets zero-padded."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "company_number": "00123456",
                "company_name": "TEST COMPANY",
            }
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = get_company("123456")

            # Verify API was called with zero-padded number
            assert "company/00123456" in mock_get.call_args.args[0]

    def test_get_company_timeout_error(self, mock_env_vars: Dict[str, str]):
        """Test get company handles timeout error."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timeout")

            result = get_company("12345678")

            assert "error" in result
            assert result["error"] == "Service temporarily unavailable. Please try again."

    def test_get_company_http_error_401(self, mock_env_vars: Dict[str, str]):
        """Test get company handles HTTP 401 authentication error."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401

            def raise_for_status():
                raise requests.HTTPError(response=mock_response)

            mock_response.raise_for_status = raise_for_status
            mock_get.return_value = mock_response

            result = get_company("12345678")

            assert "error" in result
            assert result["error"] == "Authentication error. Please check configuration."


class TestGetCompanyOfficers:
    """Test get company officers functionality."""

    def test_get_company_officers_success(self, mock_env_vars: Dict[str, str]):
        """Test successful company officers retrieval."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "total_results": 2,
                "active_count": 2,
                "resigned_count": 0,
                "items": [
                    {
                        "name": "SMITH, John",
                        "officer_role": "director",
                        "appointed_on": "2020-01-15",
                        "resigned_on": None,
                        "nationality": "British",
                        "occupation": "Director",
                        "country_of_residence": "England",
                        "address": {
                            "address_line_1": "1 Test Street",
                            "locality": "London",
                            "postal_code": "SW1A 1AA",
                        },
                    },
                    {
                        "name": "JONES, Sarah",
                        "officer_role": "secretary",
                        "appointed_on": "2020-01-15",
                        "resigned_on": None,
                        "nationality": "British",
                        "occupation": "Company Secretary",
                        "country_of_residence": "England",
                        "address": {
                            "address_line_1": "1 Test Street",
                            "locality": "London",
                            "postal_code": "SW1A 1AA",
                        },
                    },
                ],
            }
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = get_company_officers("12345678")

            # Verify API was called correctly
            mock_get.assert_called_once()
            assert "company/12345678/officers" in mock_get.call_args.args[0]

            # Verify result structure
            assert result["company_number"] == "12345678"
            assert result["total_officers"] == 2
            assert result["active_count"] == 2
            assert result["resigned_count"] == 0
            assert len(result["officers"]) == 2
            assert result["officers"][0]["name"] == "SMITH, John"
            assert result["officers"][0]["officer_role"] == "director"
            assert result["officers"][1]["name"] == "JONES, Sarah"
            assert result["data_source"] == "Companies House API"
            assert "retrieved_at" in result

    def test_get_company_officers_no_api_key(self, monkeypatch: pytest.MonkeyPatch):
        """Test get company officers without API key returns error."""
        monkeypatch.delenv("COMPANIES_HOUSE_API_KEY", raising=False)

        result = get_company_officers("12345678")

        assert "error" in result
        assert result["error"] == "Companies House API key not configured"

    def test_get_company_officers_invalid_number(self, mock_env_vars: Dict[str, str]):
        """Test get company officers with invalid company number format."""
        result = get_company_officers("INVALID")

        assert "error" in result
        assert "Invalid company number format" in result["error"]

    def test_get_company_officers_not_found(self, mock_env_vars: Dict[str, str]):
        """Test get company officers when company is not found (404 response)."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            result = get_company_officers("12345678")

            assert "error" in result
            assert result["error"] == "Company not found"

    def test_get_company_officers_with_resignations(self, mock_env_vars: Dict[str, str]):
        """Test get company officers with resigned officers."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "total_results": 2,
                "active_count": 1,
                "resigned_count": 1,
                "items": [
                    {
                        "name": "SMITH, John",
                        "officer_role": "director",
                        "appointed_on": "2020-01-15",
                        "resigned_on": None,
                    },
                    {
                        "name": "DOE, Jane",
                        "officer_role": "director",
                        "appointed_on": "2019-01-01",
                        "resigned_on": "2023-12-31",
                    },
                ],
            }
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = get_company_officers("12345678")

            assert result["total_officers"] == 2
            assert result["active_count"] == 1
            assert result["resigned_count"] == 1
            assert result["officers"][1]["resigned_on"] == "2023-12-31"


class TestGetCompanyFilingHistory:
    """Test get company filing history functionality."""

    def test_get_company_filing_history_success(self, mock_env_vars: Dict[str, str]):
        """Test successful company filing history retrieval."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "total_count": 5,
                "items": [
                    {
                        "date": "2024-01-15",
                        "category": "accounts",
                        "description": "Annual accounts made up to 31 December 2023",
                        "type": "AA",
                        "action_date": "2024-01-15",
                    },
                    {
                        "date": "2023-12-20",
                        "category": "confirmation-statement",
                        "description": "Confirmation statement made on 20 December 2023",
                        "type": "CS01",
                        "action_date": "2023-12-20",
                    },
                ],
            }
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = get_company_filing_history("12345678", items_per_page=20)

            # Verify API was called correctly
            mock_get.assert_called_once()
            assert "company/12345678/filing-history" in mock_get.call_args.args[0]
            assert mock_get.call_args.kwargs["params"]["items_per_page"] == 20

            # Verify result structure
            assert result["company_number"] == "12345678"
            assert result["total_filings"] == 5
            assert len(result["filings"]) == 2
            assert result["filings"][0]["date"] == "2024-01-15"
            assert result["filings"][0]["category"] == "accounts"
            assert result["filings"][1]["category"] == "confirmation-statement"
            assert result["data_source"] == "Companies House API"
            assert "retrieved_at" in result

    def test_get_company_filing_history_no_api_key(self, monkeypatch: pytest.MonkeyPatch):
        """Test get company filing history without API key returns error."""
        monkeypatch.delenv("COMPANIES_HOUSE_API_KEY", raising=False)

        result = get_company_filing_history("12345678")

        assert "error" in result
        assert result["error"] == "Companies House API key not configured"

    def test_get_company_filing_history_invalid_number(self, mock_env_vars: Dict[str, str]):
        """Test get company filing history with invalid company number format."""
        result = get_company_filing_history("INVALID")

        assert "error" in result
        assert "Invalid company number format" in result["error"]

    def test_get_company_filing_history_not_found(self, mock_env_vars: Dict[str, str]):
        """Test get company filing history when company is not found (404 response)."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            result = get_company_filing_history("12345678")

            assert "error" in result
            assert result["error"] == "Company not found"

    def test_get_company_filing_history_default_items_per_page(self, mock_env_vars: Dict[str, str]):
        """Test get company filing history with default items_per_page parameter."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"total_count": 0, "items": []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = get_company_filing_history("12345678")

            # Verify default items_per_page is 20
            assert mock_get.call_args.kwargs["params"]["items_per_page"] == 20

    def test_get_company_filing_history_custom_items_per_page(self, mock_env_vars: Dict[str, str]):
        """Test get company filing history with custom items_per_page parameter."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"total_count": 0, "items": []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = get_company_filing_history("12345678", items_per_page=50)

            # Verify custom items_per_page is used
            assert mock_get.call_args.kwargs["params"]["items_per_page"] == 50

    def test_get_company_filing_history_empty_results(self, mock_env_vars: Dict[str, str]):
        """Test get company filing history with no filings."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"total_count": 0, "items": []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = get_company_filing_history("12345678")

            assert result["total_filings"] == 0
            assert result["filings"] == []

    def test_get_company_filing_history_timeout_error(self, mock_env_vars: Dict[str, str]):
        """Test get company filing history handles timeout error."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timeout")

            result = get_company_filing_history("12345678")

            assert "error" in result
            assert result["error"] == "Service temporarily unavailable. Please try again."
