"""
Data validation utilities.

This module provides classes for data validation operations.

Copyright (c) 2025, Jim Schilling

This module is licensed under the MIT License.
"""

import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Union


class DataValidator:
    """
    A class for validating data against various rules and constraints.
    """

    def __init__(self):
        self._validators: Dict[str, List[Callable[[Any], bool]]] = {}
        self._custom_validators: Dict[str, Callable[[Any], bool]] = {}

    def add_validator(self, field: str, validator: Callable[[Any], bool]) -> None:
        """
        Add a validator function for a specific field.

        Args:
            field: The field name to validate
            validator: A function that takes a value and returns True if valid
        """
        if field not in self._validators:
            self._validators[field] = []
        self._validators[field].append(validator)

    def add_custom_validator(self, name: str, validator: Callable[[Any], bool]) -> None:
        """
        Add a named custom validator that can be reused.

        Args:
            name: Unique name for the validator
            validator: A function that takes a value and returns True if valid
        """
        self._custom_validators[name] = validator

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate all fields in the data dictionary.

        Args:
            data: Dictionary of field names and values to validate

        Returns:
            Dictionary mapping field names to lists of error messages
        """
        errors: Dict[str, List[str]] = {}

        for field, validators in self._validators.items():
            if field not in data:
                errors[field] = ["Field is required"]
                continue

            value = data[field]
            for validator in validators:
                if not validator(value):
                    if field not in errors:
                        errors[field] = []
                    errors[field].append(f"Validation failed for {field}")

        return errors

    @staticmethod
    def required() -> Callable[[Any], bool]:
        """Validator that checks if a value is not None or empty."""
        return lambda x: x is not None and str(x).strip() != ""

    @staticmethod
    def min_length(length: int) -> Callable[[Any], bool]:
        """Validator that checks if a string has minimum length."""
        return lambda x: len(str(x)) >= length

    @staticmethod
    def max_length(length: int) -> Callable[[Any], bool]:
        """Validator that checks if a string has maximum length."""
        return lambda x: len(str(x)) <= length

    @staticmethod
    def pattern(regex: str) -> Callable[[Any], bool]:
        """Validator that checks if a string matches a regex pattern."""
        pattern = re.compile(regex)
        return lambda x: bool(pattern.match(str(x)))

    @staticmethod
    def numeric_range(
        min_val: Union[int, float], max_val: Union[int, float]
    ) -> Callable[[Any], bool]:
        """Validator that checks if a number is within a range."""
        return lambda x: min_val <= float(x) <= max_val
