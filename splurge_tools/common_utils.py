"""
Common utility functions for splurge-tools package.

This module provides reusable utility functions and patterns to reduce
code duplication across the package.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

from pathlib import Path
from typing import Any, Callable, Iterator, TypeVar, Union
from collections.abc import Iterable

from splurge_tools.exceptions import (
    SplurgeValidationError,
    SplurgeParameterError,
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError,
    SplurgeFileEncodingError
)
from splurge_tools.validation_utils import Validator

T = TypeVar('T')


def safe_file_operation(
    file_path: Union[str, Path],
    operation: str = "access"
) -> Path:
    """
    Safely validate and convert file path with consistent error handling.
    
    Args:
        file_path: Path to validate
        operation: Description of the operation for error messages
        
    Returns:
        Validated Path object
        
    Raises:
        SplurgeFileNotFoundError: If file doesn't exist when required
        SplurgeFilePermissionError: If permission denied
        SplurgeValidationError: If path is invalid
    """
    try:
        path = Validator.is_file_path(file_path, "file_path")
        return path
    except Exception as e:
        # Re-raise with operation context
        if isinstance(e, (SplurgeFileNotFoundError, SplurgeFilePermissionError)):
            raise type(e)(
                f"Cannot {operation} file: {e.message}",
                details=e.details
            )
        raise


def standardize_column_names(
    headers: list[str],
    *,
    fill_empty: bool = True,
    prefix: str = "column_"
) -> list[str]:
    """
    Standardize column names by filling empty headers with generated names.
    
    Args:
        headers: List of header strings (may contain empty strings)
        fill_empty: Whether to fill empty headers with generated names
        prefix: Prefix for generated column names
        
    Returns:
        List of standardized column names
        
    Example:
        ["Name", "", "City"] -> ["Name", "column_1", "City"]
    """
    if not fill_empty:
        return headers
    
    result = []
    for i, header in enumerate(headers):
        if header and header.strip():
            result.append(header.strip())
        else:
            result.append(f"{prefix}{i}")
    
    return result


def ensure_minimum_columns(
    row: list[str],
    min_columns: int,
    *,
    fill_value: str = ""
) -> list[str]:
    """
    Ensure a row has at least the minimum number of columns.
    
    Args:
        row: Row data as list of strings
        min_columns: Minimum number of columns required
        fill_value: Value to use for padding missing columns
        
    Returns:
        Row data padded to minimum columns
    """
    if len(row) >= min_columns:
        return row
    
    # Pad with empty strings to reach minimum columns
    padded_row = row.copy()
    padded_row.extend([fill_value] * (min_columns - len(row)))
    return padded_row


def safe_index_access(
    items: list[T],
    index: int,
    *,
    item_name: str = "item",
    default: T | None = None
) -> T:
    """
    Safely access list item by index with helpful error messages.
    
    Args:
        items: List to access
        index: Index to access
        item_name: Name of items for error messages
        default: Default value if index out of range (if None, raises error)
        
    Returns:
        Item at index or default value
        
    Raises:
        SplurgeParameterError: If index is out of range and no default
    """
    if 0 <= index < len(items):
        return items[index]
    
    if default is not None:
        return default
    
    raise SplurgeParameterError(
        f"{item_name} index {index} out of range",
        details=f"Valid range: 0 to {len(items) - 1}, got {index}"
    )


def safe_dict_access(
    data: dict[str, T],
    key: str,
    *,
    item_name: str = "key",
    default: T | None = None
) -> T:
    """
    Safely access dictionary value by key with helpful error messages.
    
    Args:
        data: Dictionary to access
        key: Key to access
        item_name: Name of items for error messages
        default: Default value if key not found (if None, raises error)
        
    Returns:
        Value for key or default value
        
    Raises:
        SplurgeParameterError: If key not found and no default
    """
    if key in data:
        return data[key]
    
    if default is not None:
        return default
    
    available_keys = list(data.keys())[:5]  # Show first 5 keys
    key_hint = f"Available keys: {available_keys}"
    if len(data) > 5:
        key_hint += f" (and {len(data) - 5} more)"
    
    raise SplurgeParameterError(
        f"{item_name} '{key}' not found",
        details=key_hint
    )


def validate_data_structure(
    data: Any,
    *,
    expected_type: type,
    param_name: str = "data",
    allow_empty: bool = True
) -> Any:
    """
    Validate data structure with consistent error handling.
    
    Args:
        data: Data to validate
        expected_type: Expected type of the data
        param_name: Parameter name for error messages
        allow_empty: Whether empty data is allowed
        
    Returns:
        Validated data
        
    Raises:
        SplurgeParameterError: If data is wrong type
        SplurgeValidationError: If data is empty and not allowed
    """
    if data is None:
        raise SplurgeParameterError(
            f"{param_name} cannot be None",
            details=f"Expected {expected_type.__name__}, got None"
        )
    
    if not isinstance(data, expected_type):
        raise SplurgeParameterError(
            f"{param_name} must be {expected_type.__name__}, got {type(data).__name__}",
            details=f"Expected {expected_type.__name__}, received: {type(data).__name__}"
        )
    
    if not allow_empty and not data:
        raise SplurgeValidationError(
            f"{param_name} cannot be empty",
            details=f"Empty {expected_type.__name__} not allowed"
        )
    
    return data


def create_parameter_validator(
    validators: dict[str, Callable[[Any], Any]]
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """
    Create a parameter validation function from a dictionary of validators.
    
    Args:
        validators: Dictionary mapping parameter names to validation functions
        
    Returns:
        Function that validates a dictionary of parameters
        
    Example:
        validator = create_parameter_validator({
            'name': lambda x: Validator.is_non_empty_string(x, 'name'),
            'age': lambda x: Validator.is_positive_integer(x, 'age', min_value=0)
        })
        validated = validator({'name': 'John', 'age': 25})
    """
    def validate_parameters(params: dict[str, Any]) -> dict[str, Any]:
        validated = {}
        for param_name, validator in validators.items():
            if param_name in params:
                validated[param_name] = validator(params[param_name])
        return validated
    
    return validate_parameters


def batch_validate_rows(
    rows: Iterable[list[str]],
    *,
    min_columns: int | None = None,
    max_columns: int | None = None,
    skip_empty: bool = True
) -> Iterator[list[str]]:
    """
    Validate and normalize rows in a batch operation.
    
    Args:
        rows: Iterable of row data
        min_columns: Minimum columns per row (pad if needed)
        max_columns: Maximum columns per row (truncate if needed)
        skip_empty: Whether to skip completely empty rows
        
    Yields:
        Validated and normalized rows
        
    Raises:
        SplurgeValidationError: If row validation fails
    """
    for row_idx, row in enumerate(rows):
        # Skip empty rows if requested
        if skip_empty and not any(cell.strip() for cell in row):
            continue
        
        # Validate row is list of strings
        if not isinstance(row, list):
            raise SplurgeValidationError(
                f"Row {row_idx} must be a list, got {type(row).__name__}",
                details=f"Each row must be a list of strings"
            )
        
        # Ensure all cells are strings
        normalized_row = [str(cell) if cell is not None else "" for cell in row]
        
        # Apply column constraints
        if min_columns is not None and len(normalized_row) < min_columns:
            normalized_row = ensure_minimum_columns(normalized_row, min_columns)
        
        if max_columns is not None and len(normalized_row) > max_columns:
            normalized_row = normalized_row[:max_columns]
        
        yield normalized_row


def create_error_context(
    operation: str,
    *,
    file_path: Union[str, Path, None] = None,
    row_number: int | None = None,
    column_name: str | None = None,
    additional_info: str | None = None
) -> str:
    """
    Create consistent error context information.
    
    Args:
        operation: Description of the operation that failed
        file_path: File path if applicable
        row_number: Row number if applicable
        column_name: Column name if applicable
        additional_info: Additional context information
        
    Returns:
        Formatted context string
    """
    context_parts = [f"Operation: {operation}"]
    
    if file_path is not None:
        context_parts.append(f"File: {file_path}")
    
    if row_number is not None:
        context_parts.append(f"Row: {row_number}")
    
    if column_name is not None:
        context_parts.append(f"Column: {column_name}")
    
    if additional_info is not None:
        context_parts.append(f"Info: {additional_info}")
    
    return " | ".join(context_parts)


def normalize_string(
    value: str | None,
    *,
    trim: bool = True,
    handle_empty: bool = True,
    empty_default: str = ""
) -> str:
    """
    Normalize string values with consistent handling of None, empty, and whitespace.
    
    Args:
        value: String value to normalize
        trim: Whether to trim whitespace
        handle_empty: Whether to handle empty values specially
        empty_default: Default value for empty strings
        
    Returns:
        Normalized string value
    """
    if value is None:
        return empty_default if handle_empty else ""
    
    if not isinstance(value, str):
        return str(value)
    
    if trim:
        value = value.strip()
    
    if handle_empty and not value:
        return empty_default
    
    return value


def is_empty_or_none(value: Any, *, trim: bool = True) -> bool:
    """
    Check if a value is None, empty, or contains only whitespace.
    
    Args:
        value: Value to check
        trim: Whether to trim whitespace before checking
        
    Returns:
        True if value is empty, None, or whitespace-only
    """
    if value is None:
        return True
    
    if not isinstance(value, str):
        return False
    
    return not value.strip() if trim else not value


def safe_string_operation(
    value: str | None,
    operation: Callable[[str], str],
    *,
    trim: bool = True,
    handle_empty: bool = True,
    empty_default: str = ""
) -> str:
    """
    Safely apply a string operation with consistent empty value handling.
    
    Args:
        value: String value to process
        operation: Function to apply to non-empty strings
        trim: Whether to trim whitespace
        handle_empty: Whether to handle empty values specially
        empty_default: Default value for empty strings
        
    Returns:
        Processed string value
    """
    normalized = normalize_string(value, trim=trim, handle_empty=handle_empty, empty_default=empty_default)
    
    if not normalized and handle_empty:
        return empty_default
    
    return operation(normalized)


def validate_string_parameters(
    value: Any,
    param_name: str,
    *,
    allow_none: bool = False,
    allow_empty: bool = False,
    min_length: int | None = None,
    max_length: int | None = None
) -> str:
    """
    Validate string parameters with comprehensive error checking.
    
    Args:
        value: Value to validate
        param_name: Name of parameter for error messages
        allow_none: Whether None values are allowed
        allow_empty: Whether empty strings are allowed
        min_length: Minimum string length (if not None)
        max_length: Maximum string length (if not None)
        
    Returns:
        Validated string value
        
    Raises:
        SplurgeParameterError: If validation fails
    """
    if value is None:
        if not allow_none:
            raise SplurgeParameterError(
                f"{param_name} cannot be None",
                details="None values are not allowed for this parameter"
            )
        return ""
    
    if not isinstance(value, str):
        raise SplurgeParameterError(
            f"{param_name} must be a string, got {type(value).__name__}",
            details=f"Expected string, received: {repr(value)}"
        )
    
    if not value and not allow_empty:
        raise SplurgeParameterError(
            f"{param_name} cannot be empty",
            details="Empty strings are not allowed for this parameter"
        )
    
    if min_length is not None and len(value) < min_length:
        raise SplurgeParameterError(
            f"{param_name} must be at least {min_length} characters long",
            details=f"Got {len(value)} characters, minimum required: {min_length}"
        )
    
    if max_length is not None and len(value) > max_length:
        raise SplurgeParameterError(
            f"{param_name} must be at most {max_length} characters long",
            details=f"Got {len(value)} characters, maximum allowed: {max_length}"
        )
    
    return value
