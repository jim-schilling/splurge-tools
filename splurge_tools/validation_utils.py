"""
Common validation utilities for splurge-tools package.

This module provides reusable validation functions organized in a Validator class
to reduce code duplication and ensure consistent error handling across the package.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import re
from pathlib import Path
from typing import Any, Iterable, TypeVar

from splurge_tools.exceptions import (
    SplurgeParameterError,
    SplurgeRangeError,
    SplurgeFormatError,
    SplurgeValidationError
)

T = TypeVar('T')

# Sentinel value for distinguishing between None and missing values
_MISSING = object()


class Validator:
    """
    Centralized validation utilities with consistent error handling.
    
    All methods are static and follow the is_* naming convention for validation
    operations. Methods return the validated value on success or raise specific
    exceptions with helpful error messages on failure.
    """

    @staticmethod
    def is_non_empty_string(
        value: Any,
        param_name: str,
        *,
        allow_whitespace_only: bool = False
    ) -> str:
        """
        Validate that a value is a non-empty string.
        
        Args:
            value: Value to validate
            param_name: Name of the parameter for error messages
            allow_whitespace_only: Whether to allow strings with only whitespace
            
        Returns:
            The validated string value
            
        Raises:
            SplurgeParameterError: If value is not a valid non-empty string
        """
        if not isinstance(value, str):
            raise SplurgeParameterError(
                f"{param_name} must be a string, got {type(value).__name__}",
                details=f"Expected string, received: {repr(value)}"
            )
        
        if not value or (not allow_whitespace_only and not value.strip()):
            raise SplurgeParameterError(
                f"{param_name} must be a non-empty string",
                details="Empty strings and whitespace-only strings are not allowed"
            )
        
        return value

    @staticmethod
    def is_positive_integer(
        value: Any,
        param_name: str,
        *,
        min_value: int = 1,
        max_value: int | None = None
    ) -> int:
        """
        Validate that a value is a positive integer within optional bounds.
        
        Args:
            value: Value to validate
            param_name: Name of the parameter for error messages
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive), None for no limit
            
        Returns:
            The validated integer value
            
        Raises:
            SplurgeParameterError: If value is not an integer
            SplurgeRangeError: If value is outside the specified range
        """
        if not isinstance(value, int):
            raise SplurgeParameterError(
                f"{param_name} must be an integer, got {type(value).__name__}",
                details=f"Expected integer, received: {repr(value)}"
            )
        
        if value < min_value:
            raise SplurgeRangeError(
                f"{param_name} must be >= {min_value}, got {value}",
                details=f"Value {value} is below minimum allowed value {min_value}"
            )
        
        if max_value is not None and value > max_value:
            raise SplurgeRangeError(
                f"{param_name} must be <= {max_value}, got {value}",
                details=f"Value {value} exceeds maximum allowed value {max_value}"
            )
        
        return value

    @staticmethod
    def is_non_negative_integer(
        value: Any,
        param_name: str,
        *,
        max_value: int | None = None
    ) -> int:
        """
        Validate that a value is a non-negative integer (>= 0).
        
        Args:
            value: Value to validate
            param_name: Name of the parameter for error messages
            max_value: Maximum allowed value (inclusive), None for no limit
            
        Returns:
            The validated integer value
            
        Raises:
            SplurgeParameterError: If value is not an integer
            SplurgeRangeError: If value is negative or exceeds maximum
        """
        return Validator.is_positive_integer(value, param_name, min_value=0, max_value=max_value)

    @staticmethod
    def is_iterable(
        value: Any,
        param_name: str,
        *,
        allow_empty: bool = True,
        expected_type: type | None = None
    ) -> Iterable[Any]:
        """
        Validate that a value is iterable.
        
        Args:
            value: Value to validate
            param_name: Name of the parameter for error messages
            allow_empty: Whether to allow empty iterables
            expected_type: Expected type of the iterable (e.g., list, tuple)
            
        Returns:
            The validated iterable
            
        Raises:
            SplurgeParameterError: If value is not iterable or wrong type
            SplurgeValidationError: If iterable is empty and not allowed
        """
        if expected_type is not None and not isinstance(value, expected_type):
            raise SplurgeParameterError(
                f"{param_name} must be of type {expected_type.__name__}, got {type(value).__name__}",
                details=f"Expected {expected_type.__name__}, received: {type(value).__name__}"
            )
        
        try:
            iter(value)
        except TypeError:
            raise SplurgeParameterError(
                f"{param_name} must be iterable, got {type(value).__name__}",
                details=f"Value {repr(value)} is not iterable"
            )
        
        if not allow_empty and not value:
            raise SplurgeValidationError(
                f"{param_name} cannot be empty",
                details="Empty iterables are not allowed"
            )
        
        return value

    @staticmethod
    def is_range_bounds(
        lower: Any,
        upper: Any,
        *,
        lower_param: str = "lower",
        upper_param: str = "upper",
        allow_equal: bool = False
    ) -> tuple[Any, Any]:
        """
        Validate that lower and upper bounds form a valid range.
        
        Args:
            lower: Lower bound value
            upper: Upper bound value
            lower_param: Name of lower parameter for error messages
            upper_param: Name of upper parameter for error messages
            allow_equal: Whether lower == upper is allowed
            
        Returns:
            Tuple of (lower, upper) values
            
        Raises:
            SplurgeRangeError: If bounds don't form a valid range
        """
        if allow_equal:
            if lower > upper:
                raise SplurgeRangeError(
                    f"{lower_param} must be <= {upper_param}",
                    details=f"Got {lower_param}={lower}, {upper_param}={upper}"
                )
        else:
            if lower >= upper:
                raise SplurgeRangeError(
                    f"{lower_param} must be < {upper_param}",
                    details=f"Got {lower_param}={lower}, {upper_param}={upper}"
                )
        
        return lower, upper

    @staticmethod
    def is_file_path(
        value: Any,
        param_name: str,
        *,
        must_exist: bool = False,
        must_be_file: bool = False
    ) -> Path:
        """
        Validate that a value is a valid file path.
        
        Args:
            value: Value to validate (string or Path)
            param_name: Name of the parameter for error messages
            must_exist: Whether the path must exist
            must_be_file: Whether the path must be a file (not directory)
            
        Returns:
            Validated Path object
            
        Raises:
            SplurgeParameterError: If value is not a valid path type
            SplurgeValidationError: If path doesn't meet requirements
        """
        if not isinstance(value, (str, Path)):
            raise SplurgeParameterError(
                f"{param_name} must be a string or Path object, got {type(value).__name__}",
                details=f"Expected str or Path, received: {type(value).__name__}"
            )
        
        try:
            path = Path(value)
        except (TypeError, ValueError) as e:
            raise SplurgeParameterError(
                f"{param_name} is not a valid path: {value}",
                details=str(e)
            )
        
        if must_exist and not path.exists():
            raise SplurgeValidationError(
                f"{param_name} does not exist: {path}",
                details="Path must exist but was not found on filesystem"
            )
        
        if must_be_file and path.exists() and not path.is_file():
            raise SplurgeValidationError(
                f"{param_name} is not a file: {path}",
                details="Path exists but is not a regular file"
            )
        
        return path

    @staticmethod
    def is_delimiter(
        value: Any,
        param_name: str = "delimiter"
    ) -> str:
        """
        Validate that a value is a valid delimiter string.
        
        Args:
            value: Value to validate
            param_name: Name of the parameter for error messages
            
        Returns:
            The validated delimiter string
            
        Raises:
            SplurgeParameterError: If delimiter is invalid
        """
        if value is None:
            raise SplurgeParameterError(
                f"{param_name} cannot be None",
                details="Delimiter must be a non-empty string"
            )
        
        if not isinstance(value, str):
            raise SplurgeParameterError(
                f"{param_name} must be a string, got {type(value).__name__}",
                details=f"Expected string, received: {repr(value)}"
            )
        
        if not value:
            raise SplurgeParameterError(
                f"{param_name} cannot be empty",
                details="Delimiter must be at least one character"
            )
        
        return value

    @staticmethod
    def is_encoding(
        value: Any,
        param_name: str = "encoding"
    ) -> str:
        """
        Validate that a value is a valid encoding string.
        
        Args:
            value: Value to validate
            param_name: Name of the parameter for error messages
            
        Returns:
            The validated encoding string
            
        Raises:
            SplurgeParameterError: If encoding is invalid
            SplurgeFormatError: If encoding is not supported
        """
        if not isinstance(value, str):
            raise SplurgeParameterError(
                f"{param_name} must be a string, got {type(value).__name__}",
                details=f"Expected string, received: {repr(value)}"
            )
        
        if not value.strip():
            raise SplurgeParameterError(
                f"{param_name} cannot be empty or whitespace",
                details="Encoding must be a valid encoding name"
            )
        
        # Test if encoding is supported
        try:
            "test".encode(value)
        except (LookupError, ValueError) as e:
            raise SplurgeFormatError(
                f"Unsupported encoding: {value}",
                details=f"Python does not support this encoding: {str(e)}"
            )
        
        return value

    @staticmethod
    def create_helpful_error_message(
        base_message: str,
        *,
        received_value: Any = _MISSING,
        expected_type: type | str | None = None,
        valid_range: tuple[Any, Any] | None = None,
        suggestions: list[str] | None = None
    ) -> tuple[str, str]:
        """
        Create a helpful error message with context and suggestions.
        
        Args:
            base_message: Base error message
            received_value: The value that caused the error (use _MISSING to exclude from details)
            expected_type: Expected type or type description
            valid_range: Valid range as (min, max) tuple
            suggestions: List of suggestions for fixing the error
            
        Returns:
            Tuple of (message, details) for exception creation
            
        Note:
            This method properly handles falsy values (0, False, empty strings/collections)
            by using a sentinel value to distinguish between None and missing values.
        """
        details_parts = []
        
        if received_value is not _MISSING:
            details_parts.append(f"Received value: {repr(received_value)} (type: {type(received_value).__name__})")
        
        if expected_type is not None:
            if isinstance(expected_type, type):
                details_parts.append(f"Expected type: {expected_type.__name__}")
            else:
                details_parts.append(f"Expected: {expected_type}")
        
        if valid_range is not None:
            min_val, max_val = valid_range
            details_parts.append(f"Valid range: {min_val} to {max_val}")
        
        if suggestions:
            details_parts.append("Suggestions:")
            for suggestion in suggestions:
                details_parts.append(f"  - {suggestion}")
        
        details = "\n".join(details_parts) if details_parts else None
        return base_message, details

    @staticmethod
    def is_valid_email(
        value: Any,
        param_name: str
    ) -> str:
        """
        Validate that a value is a valid email address.
        
        Args:
            value: Value to validate
            param_name: Name of the parameter for error messages
            
        Returns:
            The validated email string
            
        Raises:
            SplurgeParameterError: If value is not a valid email
        """
        import re
        
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        if not isinstance(value, str):
            raise SplurgeParameterError(
                f"{param_name} must be a string, got {type(value).__name__}",
                details=f"Expected string, received: {repr(value)}"
            )
        
        if not value.strip():
            raise SplurgeParameterError(
                f"{param_name} cannot be empty",
                details="Email address cannot be empty or whitespace-only"
            )
        
        if not email_pattern.match(value.strip()):
            raise SplurgeParameterError(
                f"{param_name} is not a valid email address",
                details=f"Invalid email format: {value}"
            )
        
        return value.strip()

    @staticmethod
    def is_valid_url(
        value: Any,
        param_name: str,
        *,
        require_scheme: bool = True
    ) -> str:
        """
        Validate that a value is a valid URL.
        
        Args:
            value: Value to validate
            param_name: Name of the parameter for error messages
            require_scheme: Whether to require a scheme (http://, https://, etc.)
            
        Returns:
            The validated URL string
            
        Raises:
            SplurgeParameterError: If value is not a valid URL
        """
        from urllib.parse import urlparse
        
        if not isinstance(value, str):
            raise SplurgeParameterError(
                f"{param_name} must be a string, got {type(value).__name__}",
                details=f"Expected string, received: {repr(value)}"
            )
        
        if not value.strip():
            raise SplurgeParameterError(
                f"{param_name} cannot be empty",
                details="URL cannot be empty or whitespace-only"
            )
        
        parsed = urlparse(value.strip())
        
        if require_scheme and not parsed.scheme:
            raise SplurgeParameterError(
                f"{param_name} must include a scheme (e.g., http://, https://)",
                details=f"URL missing scheme: {value}"
            )
        
        if not parsed.netloc:
            raise SplurgeParameterError(
                f"{param_name} is not a valid URL",
                details=f"URL missing domain: {value}"
            )
        
        return value.strip()

    @staticmethod
    def is_valid_phone_number(
        value: Any,
        param_name: str,
        *,
        allow_international: bool = True
    ) -> str:
        """
        Validate that a value is a valid phone number.
        
        Args:
            value: Value to validate
            param_name: Name of the parameter for error messages
            allow_international: Whether to allow international format
            
        Returns:
            The validated phone number string
            
        Raises:
            SplurgeParameterError: If value is not a valid phone number
        """
        import re
        
        # Basic phone number patterns
        patterns = [
            r'^\+?1?\d{9,15}$',  # International format
            r'^\d{3}-\d{3}-\d{4}$',  # US format with dashes
            r'^\d{3}\.\d{3}\.\d{4}$',  # US format with dots
            r'^\d{10}$',  # US format without separators
        ]
        
        if not isinstance(value, str):
            raise SplurgeParameterError(
                f"{param_name} must be a string, got {type(value).__name__}",
                details=f"Expected string, received: {repr(value)}"
            )
        
        if not value.strip():
            raise SplurgeParameterError(
                f"{param_name} cannot be empty",
                details="Phone number cannot be empty or whitespace-only"
            )
        
        # Remove common separators for validation
        clean_number = re.sub(r'[\s\-\(\)\.]', '', value.strip())
        
        is_valid = any(re.match(pattern, clean_number) for pattern in patterns)
        
        if not is_valid:
            raise SplurgeParameterError(
                f"{param_name} is not a valid phone number",
                details=f"Invalid phone number format: {value}"
            )
        
        return value.strip()

    @staticmethod
    def is_valid_credit_card(
        value: Any,
        param_name: str
    ) -> str:
        """
        Validate that a value is a valid credit card number using Luhn algorithm.
        
        Args:
            value: Value to validate
            param_name: Name of the parameter for error messages
            
        Returns:
            The validated credit card number string
            
        Raises:
            SplurgeParameterError: If value is not a valid credit card number
        """
        import re
        
        if not isinstance(value, str):
            raise SplurgeParameterError(
                f"{param_name} must be a string, got {type(value).__name__}",
                details=f"Expected string, received: {repr(value)}"
            )
        
        # Remove spaces and dashes
        clean_number = re.sub(r'[\s\-]', '', value.strip())
        
        # Check if it's all digits and reasonable length
        if not clean_number.isdigit() or len(clean_number) < 13 or len(clean_number) > 19:
            raise SplurgeParameterError(
                f"{param_name} is not a valid credit card number",
                details=f"Invalid format or length: {value}"
            )
        
        # Luhn algorithm validation
        digits = [int(d) for d in clean_number]
        checksum = 0
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        
        checksum += sum(odd_digits)
        for d in even_digits:
            checksum += sum(divmod(d * 2, 10))
        
        if checksum % 10 != 0:
            raise SplurgeParameterError(
                f"{param_name} is not a valid credit card number",
                details=f"Failed Luhn algorithm check: {value}"
            )
        
        return value.strip()

    @staticmethod
    def is_valid_postal_code(
        value: Any,
        param_name: str,
        *,
        country: str = "US"
    ) -> str:
        """
        Validate that a value is a valid postal code.
        
        Args:
            value: Value to validate
            param_name: Name of the parameter for error messages
            country: Country code for postal code format
            
        Returns:
            The validated postal code string
            
        Raises:
            SplurgeParameterError: If value is not a valid postal code
        """
        import re
        
        patterns = {
            "US": r'^\d{5}(-\d{4})?$',
            "CA": r'^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$',
            "UK": r'^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$',
        }
        
        if not isinstance(value, str):
            raise SplurgeParameterError(
                f"{param_name} must be a string, got {type(value).__name__}",
                details=f"Expected string, received: {repr(value)}"
            )
        
        if not value.strip():
            raise SplurgeParameterError(
                f"{param_name} cannot be empty",
                details="Postal code cannot be empty or whitespace-only"
            )
        
        pattern = patterns.get(country.upper(), patterns["US"])
        
        if not re.match(pattern, value.strip(), re.IGNORECASE):
            raise SplurgeParameterError(
                f"{param_name} is not a valid postal code for {country}",
                details=f"Invalid postal code format: {value}"
            )
        
        return value.strip()


