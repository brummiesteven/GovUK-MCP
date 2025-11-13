"""Input validation utilities for Gov.uk MCP Server."""
import re
import requests
from typing import Tuple, Dict, Any


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def sanitize_api_error(error: Exception) -> Dict[str, Any]:
    """Sanitize API errors to prevent information disclosure.

    Args:
        error: The exception to sanitize

    Returns:
        Dictionary with safe error message
    """
    if isinstance(error, requests.Timeout):
        return {"error": "Service temporarily unavailable. Please try again."}
    elif isinstance(error, requests.HTTPError):
        status_code = error.response.status_code if error.response else 500
        if status_code == 404:
            return {"error": "Resource not found"}
        elif status_code in (401, 403):
            return {"error": "Authentication error. Please check configuration."}
        elif status_code == 429:
            return {"error": "Rate limit exceeded. Please try again later."}
        elif status_code >= 500:
            return {"error": "External service error. Please try again later."}
        else:
            return {"error": "Request failed. Please check your input and try again."}
    elif isinstance(error, requests.RequestException):
        return {"error": "Network error. Please check your connection and try again."}
    else:
        return {"error": "An unexpected error occurred. Please try again."}


class InputValidator:
    """Centralized input validation for all tools."""

    # UK vehicle registration patterns
    # Covers: AB12 CDE, A123 BCD, ABC 123, etc.
    UK_REGISTRATION_PATTERN = r'^[A-Z]{1,2}[0-9]{1,4}[A-Z]{0,3}$'

    # UK postcode pattern
    # Covers: SW1A 1AA, EC1A 1BB, W1A 0AX, etc.
    UK_POSTCODE_PATTERN = r'^[A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2}$'

    # Companies House number: 8 characters, alphanumeric
    COMPANY_NUMBER_PATTERN = r'^[A-Z0-9]{8}$'

    # TfL line ID: lowercase alphanumeric with hyphens
    TFL_LINE_ID_PATTERN = r'^[a-z0-9]+(-[a-z0-9]+)*$'

    # EPC certificate ID: alphanumeric with hyphens (e.g., 0000-0000-0000-0000-0000)
    EPC_CERTIFICATE_PATTERN = r'^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$'

    # CQC location ID: alphanumeric (typically 1-xxxxxxx or similar)
    CQC_LOCATION_ID_PATTERN = r'^[A-Z0-9\-]{1,20}$'

    @staticmethod
    def validate_uk_registration(registration: str) -> str:
        """Validate and clean UK vehicle registration.

        Args:
            registration: Vehicle registration number

        Returns:
            Cleaned registration (uppercase, no spaces)

        Raises:
            ValidationError: If registration format is invalid
        """
        if not registration:
            raise ValidationError("Registration number is required")

        cleaned = registration.upper().replace(" ", "")

        if len(cleaned) < 2 or len(cleaned) > 7:
            raise ValidationError("Registration must be 2-7 characters")

        if not re.match(InputValidator.UK_REGISTRATION_PATTERN, cleaned):
            raise ValidationError("Invalid UK registration format")

        return cleaned

    @staticmethod
    def validate_uk_postcode(postcode: str) -> str:
        """Validate and clean UK postcode.

        Args:
            postcode: UK postcode

        Returns:
            Cleaned postcode (uppercase, trimmed)

        Raises:
            ValidationError: If postcode format is invalid
        """
        if not postcode:
            raise ValidationError("Postcode is required")

        cleaned = postcode.upper().strip()

        if not re.match(InputValidator.UK_POSTCODE_PATTERN, cleaned):
            raise ValidationError("Invalid UK postcode format")

        return cleaned

    @staticmethod
    def validate_company_number(company_number: str) -> str:
        """Validate Companies House company number.

        Args:
            company_number: Company registration number

        Returns:
            Cleaned company number (uppercase, 8 characters, zero-padded if needed)

        Raises:
            ValidationError: If company number is invalid
        """
        if not company_number:
            raise ValidationError("Company number is required")

        cleaned = company_number.upper().strip()

        # Pad with leading zeros if needed (Companies House accepts 6-8 digit numbers)
        if len(cleaned) < 8 and cleaned.isdigit():
            cleaned = cleaned.zfill(8)

        if not re.match(InputValidator.COMPANY_NUMBER_PATTERN, cleaned):
            raise ValidationError("Invalid company number format (must be 8 alphanumeric characters)")

        return cleaned

    @staticmethod
    def validate_coordinates(lat: float, lng: float) -> Tuple[float, float]:
        """Validate latitude and longitude coordinates.

        Args:
            lat: Latitude
            lng: Longitude

        Returns:
            Tuple of (latitude, longitude) as floats

        Raises:
            ValidationError: If coordinates are out of valid range
        """
        try:
            lat_f = float(lat)
            lng_f = float(lng)
        except (ValueError, TypeError):
            raise ValidationError("Coordinates must be numeric values")

        if not (-90 <= lat_f <= 90):
            raise ValidationError("Latitude must be between -90 and 90")

        if not (-180 <= lng_f <= 180):
            raise ValidationError("Longitude must be between -180 and 180")

        return lat_f, lng_f

    @staticmethod
    def sanitize_query(query: str, max_length: int = 200) -> str:
        """Sanitize search query string.

        Removes control characters and limits length.

        Args:
            query: Search query
            max_length: Maximum allowed length

        Returns:
            Sanitized query string

        Raises:
            ValidationError: If query is empty or invalid
        """
        if not query:
            raise ValidationError("Query is required")

        # Remove control characters (ASCII < 32)
        sanitized = "".join(char for char in query if ord(char) >= 32)

        # Trim to max length
        sanitized = sanitized[:max_length].strip()

        if not sanitized:
            raise ValidationError("Query contains no valid characters")

        return sanitized

    @staticmethod
    def validate_date_format(date_str: str, format_name: str = "YYYY-MM-DD") -> str:
        """Validate date string format.

        Args:
            date_str: Date string
            format_name: Expected format description (for error messages)

        Returns:
            Original date string if valid

        Raises:
            ValidationError: If date format is invalid
        """
        if not date_str:
            raise ValidationError("Date is required")

        # Basic YYYY-MM-DD validation
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'

        if not re.match(date_pattern, date_str):
            raise ValidationError(f"Invalid date format. Expected {format_name}")

        return date_str

    @staticmethod
    def validate_tfl_line_id(line_id: str) -> str:
        """Validate TfL line ID.

        Args:
            line_id: TfL line identifier (e.g., 'central', 'northern', 'piccadilly')

        Returns:
            Cleaned line ID (lowercase)

        Raises:
            ValidationError: If line ID format is invalid
        """
        if not line_id:
            raise ValidationError("Line ID is required")

        cleaned = line_id.lower().strip()

        if not re.match(InputValidator.TFL_LINE_ID_PATTERN, cleaned):
            raise ValidationError("Invalid TfL line ID format")

        # Validate against known TfL lines
        valid_lines = {
            'bakerloo', 'central', 'circle', 'district', 'dlr',
            'elizabeth', 'hammersmith-city', 'jubilee', 'london-overground',
            'metropolitan', 'northern', 'piccadilly', 'victoria', 'waterloo-city'
        }

        if cleaned not in valid_lines:
            raise ValidationError(f"Unknown TfL line ID. Valid lines: {', '.join(sorted(valid_lines))}")

        return cleaned

    @staticmethod
    def validate_epc_certificate_id(certificate_id: str) -> str:
        """Validate EPC certificate ID.

        Args:
            certificate_id: EPC certificate identifier (e.g., '0000-0000-0000-0000-0000')

        Returns:
            Cleaned certificate ID (uppercase)

        Raises:
            ValidationError: If certificate ID format is invalid
        """
        if not certificate_id:
            raise ValidationError("Certificate ID is required")

        cleaned = certificate_id.upper().strip()

        if not re.match(InputValidator.EPC_CERTIFICATE_PATTERN, cleaned):
            raise ValidationError("Invalid EPC certificate ID format (expected: XXXX-XXXX-XXXX-XXXX-XXXX)")

        return cleaned

    @staticmethod
    def validate_cqc_location_id(location_id: str) -> str:
        """Validate CQC location ID.

        Args:
            location_id: CQC location identifier

        Returns:
            Cleaned location ID (uppercase)

        Raises:
            ValidationError: If location ID format is invalid
        """
        if not location_id:
            raise ValidationError("Location ID is required")

        cleaned = location_id.upper().strip()

        if not re.match(InputValidator.CQC_LOCATION_ID_PATTERN, cleaned):
            raise ValidationError("Invalid CQC location ID format")

        if len(cleaned) > 20:
            raise ValidationError("CQC location ID must not exceed 20 characters")

        return cleaned

    @staticmethod
    def validate_alphanumeric_id(id_value: str, name: str = "ID", max_length: int = 50) -> str:
        """Validate generic alphanumeric identifier.

        Args:
            id_value: The ID value to validate
            name: Human-readable name for error messages
            max_length: Maximum allowed length

        Returns:
            Cleaned ID value

        Raises:
            ValidationError: If ID format is invalid
        """
        if not id_value:
            raise ValidationError(f"{name} is required")

        cleaned = id_value.strip()

        if len(cleaned) > max_length:
            raise ValidationError(f"{name} must not exceed {max_length} characters")

        # Allow only alphanumeric, hyphens, and underscores
        if not re.match(r'^[A-Za-z0-9\-_]+$', cleaned):
            raise ValidationError(f"{name} must contain only alphanumeric characters, hyphens, and underscores")

        return cleaned
