"""
Data validation utilities.

This module provides classes for data validation operations.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import re
from typing import Any, Callable, Dict, List

from splurge_tools.protocols import DataValidatorProtocol


class DataValidator(DataValidatorProtocol):
    """
    A class for validating data against various rules and constraints.
    
    This class implements the DataValidatorProtocol interface, providing
    a consistent interface for data validation operations.
    """

    def __init__(self) -> None:
        self._validators: Dict[str, List[Callable[[Any], bool]]] = {}
        self._custom_validators: Dict[str, Callable[[Any], bool]] = {}
        self._errors: List[str] = []

    def add_validator(
        self,
        field: str,
        validator: Callable[[Any], bool]
    ) -> None:
        """
        Add a validator function for a specific field.

        Args:
            field: The field name to validate
            validator: A function that takes a value and returns True if valid
        """
        if field not in self._validators:
            self._validators[field] = []
        self._validators[field].append(validator)

    def add_custom_validator(
        self,
        name: str,
        validator: Callable[[Any], bool]
    ) -> None:
        """
        Add a named custom validator that can be reused.

        Args:
            name: Unique name for the validator
            validator: A function that takes a value and returns True if valid
        """
        self._custom_validators[name] = validator

    def validate(
        self,
        data: Any
    ) -> bool:
        """
        Validate the given data.

        Args:
            data: Data to validate (can be dict, list, or any other type)

        Returns:
            True if data is valid, False otherwise
        """
        self.clear_errors()
        
        if isinstance(data, dict):
            return self._validate_dict(data)
        elif isinstance(data, list):
            return self._validate_list(data)
        else:
            # For non-dict/list data, check if any validators exist
            if not self._validators:
                return True  # No validators means everything is valid
            
            # Apply validators to the data itself
            for field, validators in self._validators.items():
                for validator in validators:
                    if not validator(data):
                        self._errors.append(f"Validation failed for {field}")
                        return False
            return True

    def _validate_dict(
        self,
        data: Dict[str, Any]
    ) -> bool:
        """Validate dictionary data."""
        is_valid = True
        
        for field, validators in self._validators.items():
            if field not in data:
                self._errors.append(f"Field '{field}' is required")
                is_valid = False
                continue

            value = data[field]
            for validator in validators:
                if not validator(value):
                    self._errors.append(f"Validation failed for field '{field}'")
                    is_valid = False
                    break
        
        return is_valid

    def _validate_list(
        self,
        data: List[Any]
    ) -> bool:
        """Validate list data."""
        is_valid = True
        
        for field, validators in self._validators.items():
            try:
                index = int(field)
                if index >= len(data):
                    self._errors.append(f"Index {index} is out of range")
                    is_valid = False
                    continue
                
                value = data[index]
                for validator in validators:
                    if not validator(value):
                        self._errors.append(f"Validation failed for index {index}")
                        is_valid = False
                        break
            except ValueError:
                # Field is not a valid index, skip
                continue
        
        return is_valid

    def get_errors(self) -> List[str]:
        """
        Get list of validation errors.
        
        Returns:
            List of error messages from the last validation
        """
        return self._errors.copy()

    def clear_errors(self) -> None:
        """Clear all validation errors."""
        self._errors.clear()

    def validate_detailed(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Validate all fields in the data dictionary and return detailed errors.

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

    def validate_with_custom_rules(
        self,
        data: Dict[str, Any],
        rules: Dict[str, List[str]]
    ) -> bool:
        """
        Validate data using predefined validation rules.
        
        Args:
            data: Dictionary of field names and values to validate
            rules: Dictionary mapping field names to lists of rule names
            
        Returns:
            True if all validations pass, False otherwise
        """
        self.clear_errors()
        
        for field, rule_names in rules.items():
            if field not in data:
                self._errors.append(f"Field '{field}' is required")
                continue
                
            value = data[field]
            for rule_name in rule_names:
                if rule_name in self._custom_validators:
                    if not self._custom_validators[rule_name](value):
                        self._errors.append(f"Rule '{rule_name}' failed for field '{field}'")
                else:
                    self._errors.append(f"Unknown validation rule: {rule_name}")
        
        return len(self._errors) == 0

    def add_field_validators(
        self,
        field: str,
        *validators: Callable[[Any], bool]
    ) -> None:
        """
        Add multiple validators for a field at once.
        
        Args:
            field: The field name to validate
            *validators: Variable number of validator functions
        """
        if field not in self._validators:
            self._validators[field] = []
        self._validators[field].extend(validators)

    def remove_field_validators(
        self,
        field: str
    ) -> None:
        """
        Remove all validators for a specific field.
        
        Args:
            field: The field name to remove validators for
        """
        if field in self._validators:
            del self._validators[field]

    def get_field_validators(
        self,
        field: str
    ) -> List[Callable[[Any], bool]]:
        """
        Get all validators for a specific field.
        
        Args:
            field: The field name to get validators for
            
        Returns:
            List of validator functions for the field
        """
        return self._validators.get(field, []).copy()

    @staticmethod
    def required() -> Callable[[Any], bool]:
        """Validator that checks if a value is not None or empty."""
        return lambda x: x is not None and str(x).strip() != ""

    @staticmethod
    def min_length(
        length: int
    ) -> Callable[[Any], bool]:
        """Validator that checks if a string has minimum length."""
        return lambda x: len(str(x)) >= length

    @staticmethod
    def max_length(
        length: int
    ) -> Callable[[Any], bool]:
        """Validator that checks if a string has maximum length."""
        return lambda x: len(str(x)) <= length

    @staticmethod
    def pattern(
        regex: str
    ) -> Callable[[Any], bool]:
        """Validator that checks if a string matches a regex pattern."""
        pattern = re.compile(regex)
        return lambda x: bool(pattern.match(str(x)))

    @staticmethod
    def numeric_range(
        min_val: int | float,
        max_val: int | float
    ) -> Callable[[Any], bool]:
        """Validator that checks if a number is within a range."""
        return lambda x: min_val <= float(x) <= max_val


