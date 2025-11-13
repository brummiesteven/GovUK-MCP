"""Tests for input validation module.

This module tests all InputValidator methods with both valid and invalid inputs
to ensure proper validation and error handling.
"""

import pytest
import requests
from gov_uk_mcp.validation import (
    InputValidator,
    ValidationError,
    sanitize_api_error,
)


class TestValidateUKRegistration:
    """Test UK vehicle registration validation."""

    def test_valid_registration_standard_format(self):
        """Test validation of standard UK registration format (AB12 CDE)."""
        result = InputValidator.validate_uk_registration("AB12 CDE")
        assert result == "AB12CDE"

    def test_valid_registration_no_spaces(self):
        """Test validation of registration without spaces."""
        result = InputValidator.validate_uk_registration("AB12CDE")
        assert result == "AB12CDE"

    def test_valid_registration_lowercase(self):
        """Test validation converts lowercase to uppercase."""
        result = InputValidator.validate_uk_registration("ab12cde")
        assert result == "AB12CDE"

    def test_valid_registration_old_format(self):
        """Test validation of older format (A123 BCD)."""
        result = InputValidator.validate_uk_registration("A123BCD")
        assert result == "A123BCD"

    def test_valid_registration_dateless_format(self):
        """Test validation of dateless format (ABC 123)."""
        result = InputValidator.validate_uk_registration("ABC123")
        assert result == "ABC123"

    def test_empty_registration(self):
        """Test that empty registration raises ValidationError."""
        with pytest.raises(ValidationError, match="Registration number is required"):
            InputValidator.validate_uk_registration("")

    def test_none_registration(self):
        """Test that None registration raises ValidationError."""
        with pytest.raises(ValidationError, match="Registration number is required"):
            InputValidator.validate_uk_registration(None)

    def test_registration_too_short(self):
        """Test that registration shorter than 2 characters raises ValidationError."""
        with pytest.raises(ValidationError, match="Registration must be 2-7 characters"):
            InputValidator.validate_uk_registration("A")

    def test_registration_too_long(self):
        """Test that registration longer than 7 characters raises ValidationError."""
        with pytest.raises(ValidationError, match="Registration must be 2-7 characters"):
            InputValidator.validate_uk_registration("ABCD12345")

    def test_invalid_registration_format(self):
        """Test that invalid format (numbers first) raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid UK registration format"):
            InputValidator.validate_uk_registration("123ABC")

    def test_invalid_registration_special_characters(self):
        """Test that special characters raise ValidationError."""
        with pytest.raises(ValidationError, match="Invalid UK registration format"):
            InputValidator.validate_uk_registration("AB12-CDE")


class TestValidateUKPostcode:
    """Test UK postcode validation."""

    def test_valid_postcode_standard_format(self):
        """Test validation of standard postcode format (SW1A 1AA)."""
        result = InputValidator.validate_uk_postcode("SW1A 1AA")
        assert result == "SW1A 1AA"

    def test_valid_postcode_no_space(self):
        """Test validation of postcode without space."""
        result = InputValidator.validate_uk_postcode("SW1A1AA")
        assert result == "SW1A1AA"

    def test_valid_postcode_lowercase(self):
        """Test validation converts lowercase to uppercase."""
        result = InputValidator.validate_uk_postcode("sw1a 1aa")
        assert result == "SW1A 1AA"

    def test_valid_postcode_with_extra_whitespace(self):
        """Test validation removes leading/trailing whitespace."""
        result = InputValidator.validate_uk_postcode("  SW1A 1AA  ")
        assert result == "SW1A 1AA"

    def test_valid_postcode_short_format(self):
        """Test validation of short postcode format (W1A 0AX)."""
        result = InputValidator.validate_uk_postcode("W1A 0AX")
        assert result == "W1A 0AX"

    def test_valid_postcode_double_digit_area(self):
        """Test validation of double-digit area code (EC1A 1BB)."""
        result = InputValidator.validate_uk_postcode("EC1A 1BB")
        assert result == "EC1A 1BB"

    def test_empty_postcode(self):
        """Test that empty postcode raises ValidationError."""
        with pytest.raises(ValidationError, match="Postcode is required"):
            InputValidator.validate_uk_postcode("")

    def test_none_postcode(self):
        """Test that None postcode raises ValidationError."""
        with pytest.raises(ValidationError, match="Postcode is required"):
            InputValidator.validate_uk_postcode(None)

    def test_invalid_postcode_format(self):
        """Test that invalid format raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid UK postcode format"):
            InputValidator.validate_uk_postcode("INVALID")

    def test_invalid_postcode_too_many_numbers(self):
        """Test that too many numbers raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid UK postcode format"):
            InputValidator.validate_uk_postcode("SW1A 12345")

    def test_invalid_postcode_wrong_structure(self):
        """Test that wrong structure raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid UK postcode format"):
            InputValidator.validate_uk_postcode("1234 5678")


class TestValidateCompanyNumber:
    """Test Companies House company number validation."""

    def test_valid_company_number_eight_digits(self):
        """Test validation of 8-digit company number."""
        result = InputValidator.validate_company_number("12345678")
        assert result == "12345678"

    def test_valid_company_number_with_letters(self):
        """Test validation of company number with letters."""
        result = InputValidator.validate_company_number("SC123456")
        assert result == "SC123456"

    def test_valid_company_number_lowercase(self):
        """Test validation converts lowercase to uppercase."""
        result = InputValidator.validate_company_number("sc123456")
        assert result == "SC123456"

    def test_valid_company_number_six_digits_padded(self):
        """Test that 6-digit number is zero-padded to 8 digits."""
        result = InputValidator.validate_company_number("123456")
        assert result == "00123456"

    def test_valid_company_number_seven_digits_padded(self):
        """Test that 7-digit number is zero-padded to 8 digits."""
        result = InputValidator.validate_company_number("1234567")
        assert result == "01234567"

    def test_valid_company_number_with_whitespace(self):
        """Test validation removes whitespace."""
        result = InputValidator.validate_company_number("  12345678  ")
        assert result == "12345678"

    def test_empty_company_number(self):
        """Test that empty company number raises ValidationError."""
        with pytest.raises(ValidationError, match="Company number is required"):
            InputValidator.validate_company_number("")

    def test_none_company_number(self):
        """Test that None company number raises ValidationError."""
        with pytest.raises(ValidationError, match="Company number is required"):
            InputValidator.validate_company_number(None)

    def test_invalid_company_number_too_short(self):
        """Test that too short non-padded number raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid company number format"):
            InputValidator.validate_company_number("12ABC")

    def test_invalid_company_number_too_long(self):
        """Test that too long company number raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid company number format"):
            InputValidator.validate_company_number("123456789")

    def test_invalid_company_number_special_characters(self):
        """Test that special characters raise ValidationError."""
        with pytest.raises(ValidationError, match="Invalid company number format"):
            InputValidator.validate_company_number("1234-5678")


class TestValidateCoordinates:
    """Test coordinate validation."""

    def test_valid_coordinates_uk_location(self):
        """Test validation of valid UK coordinates."""
        lat, lng = InputValidator.validate_coordinates(51.5014, -0.1419)
        assert lat == 51.5014
        assert lng == -0.1419

    def test_valid_coordinates_as_strings(self):
        """Test validation converts string coordinates to floats."""
        lat, lng = InputValidator.validate_coordinates("51.5014", "-0.1419")
        assert lat == 51.5014
        assert lng == -0.1419

    def test_valid_coordinates_boundary_values(self):
        """Test validation of boundary coordinate values."""
        lat, lng = InputValidator.validate_coordinates(90, 180)
        assert lat == 90.0
        assert lng == 180.0

        lat, lng = InputValidator.validate_coordinates(-90, -180)
        assert lat == -90.0
        assert lng == -180.0

    def test_invalid_latitude_too_high(self):
        """Test that latitude > 90 raises ValidationError."""
        with pytest.raises(ValidationError, match="Latitude must be between -90 and 90"):
            InputValidator.validate_coordinates(91, 0)

    def test_invalid_latitude_too_low(self):
        """Test that latitude < -90 raises ValidationError."""
        with pytest.raises(ValidationError, match="Latitude must be between -90 and 90"):
            InputValidator.validate_coordinates(-91, 0)

    def test_invalid_longitude_too_high(self):
        """Test that longitude > 180 raises ValidationError."""
        with pytest.raises(ValidationError, match="Longitude must be between -180 and 180"):
            InputValidator.validate_coordinates(0, 181)

    def test_invalid_longitude_too_low(self):
        """Test that longitude < -180 raises ValidationError."""
        with pytest.raises(ValidationError, match="Longitude must be between -180 and 180"):
            InputValidator.validate_coordinates(0, -181)

    def test_invalid_coordinates_non_numeric(self):
        """Test that non-numeric coordinates raise ValidationError."""
        with pytest.raises(ValidationError, match="Coordinates must be numeric values"):
            InputValidator.validate_coordinates("abc", "def")

    def test_invalid_coordinates_none_value(self):
        """Test that None coordinates raise ValidationError."""
        with pytest.raises(ValidationError, match="Coordinates must be numeric values"):
            InputValidator.validate_coordinates(None, None)


class TestSanitizeQuery:
    """Test query sanitization."""

    def test_valid_query(self):
        """Test sanitization of valid query string."""
        result = InputValidator.sanitize_query("test company")
        assert result == "test company"

    def test_query_with_leading_trailing_whitespace(self):
        """Test that leading/trailing whitespace is removed."""
        result = InputValidator.sanitize_query("  test query  ")
        assert result == "test query"

    def test_query_with_control_characters(self):
        """Test that control characters are removed."""
        result = InputValidator.sanitize_query("test\x00\x01query")
        assert result == "testquery"

    def test_query_exceeding_max_length(self):
        """Test that query is truncated to max length."""
        long_query = "a" * 300
        result = InputValidator.sanitize_query(long_query, max_length=200)
        assert len(result) == 200

    def test_query_with_special_characters_preserved(self):
        """Test that valid special characters are preserved."""
        result = InputValidator.sanitize_query("test & company @ location!")
        assert result == "test & company @ location!"

    def test_empty_query(self):
        """Test that empty query raises ValidationError."""
        with pytest.raises(ValidationError, match="Query is required"):
            InputValidator.sanitize_query("")

    def test_none_query(self):
        """Test that None query raises ValidationError."""
        with pytest.raises(ValidationError, match="Query is required"):
            InputValidator.sanitize_query(None)

    def test_query_only_control_characters(self):
        """Test that query with only control characters raises ValidationError."""
        with pytest.raises(ValidationError, match="Query contains no valid characters"):
            InputValidator.sanitize_query("\x00\x01\x02")

    def test_query_whitespace_only(self):
        """Test that whitespace-only query raises ValidationError."""
        with pytest.raises(ValidationError, match="Query contains no valid characters"):
            InputValidator.sanitize_query("   ")


class TestValidateDateFormat:
    """Test date format validation."""

    def test_valid_date_format(self):
        """Test validation of valid date in YYYY-MM-DD format."""
        result = InputValidator.validate_date_format("2024-01-15")
        assert result == "2024-01-15"

    def test_valid_date_boundary_values(self):
        """Test validation of boundary date values."""
        result = InputValidator.validate_date_format("2024-12-31")
        assert result == "2024-12-31"

    def test_invalid_date_format_wrong_separator(self):
        """Test that wrong separator raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid date format"):
            InputValidator.validate_date_format("2024/01/15")

    def test_invalid_date_format_wrong_order(self):
        """Test that wrong date order raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid date format"):
            InputValidator.validate_date_format("15-01-2024")

    def test_invalid_date_format_short_year(self):
        """Test that short year format raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid date format"):
            InputValidator.validate_date_format("24-01-15")

    def test_invalid_date_format_single_digit_month(self):
        """Test that single digit month raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid date format"):
            InputValidator.validate_date_format("2024-1-15")

    def test_invalid_date_format_single_digit_day(self):
        """Test that single digit day raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid date format"):
            InputValidator.validate_date_format("2024-01-5")

    def test_empty_date(self):
        """Test that empty date raises ValidationError."""
        with pytest.raises(ValidationError, match="Date is required"):
            InputValidator.validate_date_format("")

    def test_none_date(self):
        """Test that None date raises ValidationError."""
        with pytest.raises(ValidationError, match="Date is required"):
            InputValidator.validate_date_format(None)


class TestSanitizeAPIError:
    """Test API error sanitization."""

    def test_sanitize_timeout_error(self):
        """Test sanitization of timeout error."""
        error = requests.Timeout("Connection timeout")
        result = sanitize_api_error(error)
        assert result == {"error": "Service temporarily unavailable. Please try again."}

    def test_sanitize_404_error(self):
        """Test sanitization of 404 HTTP error."""
        response = requests.Response()
        response.status_code = 404
        error = requests.HTTPError(response=response)
        result = sanitize_api_error(error)
        assert result == {"error": "Resource not found"}

    def test_sanitize_401_error(self):
        """Test sanitization of 401 authentication error."""
        response = requests.Response()
        response.status_code = 401
        error = requests.HTTPError(response=response)
        result = sanitize_api_error(error)
        assert result == {"error": "Authentication error. Please check configuration."}

    def test_sanitize_403_error(self):
        """Test sanitization of 403 forbidden error."""
        response = requests.Response()
        response.status_code = 403
        error = requests.HTTPError(response=response)
        result = sanitize_api_error(error)
        assert result == {"error": "Authentication error. Please check configuration."}

    def test_sanitize_429_error(self):
        """Test sanitization of 429 rate limit error."""
        response = requests.Response()
        response.status_code = 429
        error = requests.HTTPError(response=response)
        result = sanitize_api_error(error)
        assert result == {"error": "Rate limit exceeded. Please try again later."}

    def test_sanitize_500_error(self):
        """Test sanitization of 500 server error."""
        response = requests.Response()
        response.status_code = 500
        error = requests.HTTPError(response=response)
        result = sanitize_api_error(error)
        assert result == {"error": "External service error. Please try again later."}

    def test_sanitize_503_error(self):
        """Test sanitization of 503 service unavailable error."""
        response = requests.Response()
        response.status_code = 503
        error = requests.HTTPError(response=response)
        result = sanitize_api_error(error)
        assert result == {"error": "External service error. Please try again later."}

    def test_sanitize_generic_http_error(self):
        """Test sanitization of generic HTTP error."""
        response = requests.Response()
        response.status_code = 400
        error = requests.HTTPError(response=response)
        result = sanitize_api_error(error)
        assert result == {"error": "Request failed. Please check your input and try again."}

    def test_sanitize_network_error(self):
        """Test sanitization of network error."""
        error = requests.RequestException("Network error")
        result = sanitize_api_error(error)
        assert result == {"error": "Network error. Please check your connection and try again."}

    def test_sanitize_generic_error(self):
        """Test sanitization of generic exception."""
        error = ValueError("Some internal error")
        result = sanitize_api_error(error)
        assert result == {"error": "An unexpected error occurred. Please try again."}

    def test_sanitize_http_error_no_response(self):
        """Test sanitization of HTTP error without response object."""
        error = requests.HTTPError()
        result = sanitize_api_error(error)
        assert result == {"error": "External service error. Please try again later."}
