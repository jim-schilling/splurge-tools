"""
Comprehensive unit tests for DataValidator class to improve coverage.
"""

import unittest

import pytest

from splurge_tools.data_validator import DataValidator
from splurge_tools.protocols import DataValidatorProtocol


class TestDataValidatorComprehensive(unittest.TestCase):
    """Comprehensive test cases for DataValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = DataValidator()

    def test_validate_non_dict_list_data_with_validators(self):
        """Test validate method with non-dict/list data when validators exist."""
        # Add a validator for a field
        self.validator.add_validator("test_field", lambda x: isinstance(x, str))

        # Test with string data (should pass)
        result = self.validator.validate("hello")
        assert result
        assert len(self.validator.get_errors()) == 0

        # Test with non-string data (should fail)
        result = self.validator.validate(123)
        assert not result
        assert len(self.validator.get_errors()) > 0

    def test_validate_non_dict_list_data_without_validators(self):
        """Test validate method with non-dict/list data when no validators exist."""
        # No validators added
        result = self.validator.validate("hello")
        assert result  # Should pass when no validators exist

        result = self.validator.validate(123)
        assert result  # Should pass when no validators exist

        result = self.validator.validate(None)
        assert result  # Should pass when no validators exist

    def test_validate_dict_with_missing_required_fields(self):
        """Test validate method with dictionary missing required fields."""
        self.validator.add_validator("name", lambda x: len(x) > 0)
        self.validator.add_validator("age", lambda x: isinstance(x, int) and x > 0)

        # Test with missing fields
        data = {"name": "John"}  # Missing age
        result = self.validator.validate(data)
        assert not result
        errors = self.validator.get_errors()
        assert "Field 'age' is required" in errors

    def test_validate_dict_with_invalid_values(self):
        """Test validate method with dictionary containing invalid values."""
        self.validator.add_validator("name", lambda x: len(x) > 0)
        self.validator.add_validator("age", lambda x: isinstance(x, int) and x > 0)

        # Test with invalid values
        data = {"name": "", "age": -5}  # Empty name, negative age
        result = self.validator.validate(data)
        assert not result
        errors = self.validator.get_errors()
        assert "Validation failed for field 'name'" in errors

    def test_validate_list_with_valid_indices(self):
        """Test validate method with list data using valid indices."""
        self.validator.add_validator("0", lambda x: isinstance(x, str))  # First element should be string
        self.validator.add_validator("1", lambda x: isinstance(x, int))  # Second element should be int

        # Test with valid list
        data = ["hello", 42]
        result = self.validator.validate(data)
        assert result
        assert len(self.validator.get_errors()) == 0

    def test_validate_list_with_out_of_range_indices(self):
        """Test validate method with list data using out-of-range indices."""
        self.validator.add_validator("5", lambda x: True)  # Index 5 doesn't exist

        # Test with short list
        data = ["hello", "world"]
        result = self.validator.validate(data)
        assert not result
        errors = self.validator.get_errors()
        assert "Index 5 is out of range" in errors

    def test_validate_list_with_invalid_indices(self):
        """Test validate method with list data using invalid index names."""
        self.validator.add_validator("invalid", lambda x: True)  # Not a valid index

        # Test with list - should skip invalid indices
        data = ["hello", "world"]
        result = self.validator.validate(data)
        assert result  # Should pass because invalid indices are skipped
        assert len(self.validator.get_errors()) == 0

    def test_validate_list_with_failing_validators(self):
        """Test validate method with list data where validators fail."""
        self.validator.add_validator("0", lambda x: isinstance(x, int))  # First element should be int
        self.validator.add_validator("1", lambda x: len(x) > 5)  # Second element should be long string

        # Test with failing validators
        data = ["hello", "short"]
        result = self.validator.validate(data)
        assert not result
        errors = self.validator.get_errors()
        assert "Validation failed for index 0" in errors

    def test_multiple_validators_per_field(self):
        """Test multiple validators per field."""
        self.validator.add_validator("name", lambda x: isinstance(x, str))
        self.validator.add_validator("name", lambda x: len(x) > 0)
        self.validator.add_validator("name", lambda x: x.isalpha())

        # Test with valid data
        data = {"name": "John"}
        result = self.validator.validate(data)
        assert result

        # Test with invalid data (fails second validator)
        data = {"name": ""}
        result = self.validator.validate(data)
        assert not result

        # Test with invalid data (fails third validator)
        data = {"name": "John123"}
        result = self.validator.validate(data)
        assert not result

    def test_custom_validators(self):
        """Test custom validators functionality."""
        # Add a custom validator
        self.validator.add_custom_validator("email", lambda x: "@" in str(x))

        # Test that custom validators don't affect regular validation
        data = {"name": "John"}
        result = self.validator.validate(data)
        assert result  # Should pass because no regular validators

    def test_clear_errors_functionality(self):
        """Test clear_errors method functionality."""
        # Add a validator and trigger an error
        self.validator.add_validator("name", lambda x: len(x) > 0)
        data = {"name": ""}
        result = self.validator.validate(data)
        assert not result
        assert len(self.validator.get_errors()) > 0

        # Clear errors
        self.validator.clear_errors()
        assert len(self.validator.get_errors()) == 0

        # Validate again - should work normally
        data = {"name": "John"}
        result = self.validator.validate(data)
        assert result

    def test_get_errors_returns_copy(self):
        """Test that get_errors returns a copy of the error list."""
        # Add a validator and trigger an error
        self.validator.add_validator("name", lambda x: len(x) > 0)
        data = {"name": ""}
        self.validator.validate(data)

        # Get errors and modify the returned list
        errors = self.validator.get_errors()
        original_length = len(errors)
        errors.append("extra error")

        # Get errors again - should not include the extra error
        errors_again = self.validator.get_errors()
        assert len(errors_again) == original_length
        assert "extra error" not in errors_again

    def test_validate_detailed_method(self):
        """Test the validate_detailed method for backward compatibility."""
        self.validator.add_validator("name", lambda x: len(x) > 0)
        self.validator.add_validator("age", lambda x: isinstance(x, int))

        # Test with valid data
        data = {"name": "John", "age": 25}
        result = self.validator.validate_detailed(data)
        assert isinstance(result, dict)
        assert len(result) == 0  # No errors

        # Test with invalid data
        data = {"name": "", "age": "not_a_number"}
        result = self.validator.validate_detailed(data)
        assert isinstance(result, dict)
        assert len(result) > 0  # Has errors

        # Test with multiple validators for same field to cover missing lines
        self.validator.add_validator("name", lambda x: x.isalpha())  # Add second validator
        data = {"name": "John123"}  # Fails second validator
        result = self.validator.validate_detailed(data)
        assert isinstance(result, dict)
        assert "name" in result
        assert len(result["name"]) > 0  # Should have error messages

    def test_validate_with_custom_rules(self):
        """Test validate_with_custom_rules method."""
        # Add custom validators
        self.validator.add_custom_validator("email", lambda x: "@" in str(x))
        self.validator.add_custom_validator("positive", lambda x: float(x) > 0)
        self.validator.add_custom_validator("length_3", lambda x: len(str(x)) == 3)

        # Test with valid data
        data = {"email": "test@example.com", "age": "25", "code": "ABC"}
        rules = {
            "email": ["email"],
            "age": ["positive"],
            "code": ["length_3"],
        }
        result = self.validator.validate_with_custom_rules(data, rules)
        assert result
        assert len(self.validator.get_errors()) == 0

        # Test with invalid data
        data = {"email": "invalid_email", "age": "-5", "code": "ABCD"}
        result = self.validator.validate_with_custom_rules(data, rules)
        assert not result
        errors = self.validator.get_errors()
        assert "Rule 'email' failed for field 'email'" in errors
        assert "Rule 'positive' failed for field 'age'" in errors
        assert "Rule 'length_3' failed for field 'code'" in errors

        # Test with missing required field
        data = {"email": "test@example.com"}  # Missing age and code
        result = self.validator.validate_with_custom_rules(data, rules)
        assert not result
        errors = self.validator.get_errors()
        assert "Field 'age' is required" in errors
        assert "Field 'code' is required" in errors

        # Test with unknown rule
        data = {"email": "test@example.com"}
        rules = {"email": ["unknown_rule"]}
        result = self.validator.validate_with_custom_rules(data, rules)
        assert not result
        errors = self.validator.get_errors()
        assert "Unknown validation rule: unknown_rule" in errors

    def test_add_field_validators(self):
        """Test add_field_validators method."""
        # Add multiple validators at once
        self.validator.add_field_validators(
            "name",
            lambda x: isinstance(x, str),
            lambda x: len(x) > 0,
            lambda x: x.isalpha(),
        )

        # Test with valid data
        data = {"name": "John"}
        result = self.validator.validate(data)
        assert result

        # Test with invalid data (fails first validator)
        data = {"name": 123}
        result = self.validator.validate(data)
        assert not result

        # Test with invalid data (fails second validator)
        data = {"name": ""}
        result = self.validator.validate(data)
        assert not result

        # Test with invalid data (fails third validator)
        data = {"name": "John123"}
        result = self.validator.validate(data)
        assert not result

        # Test adding to existing field
        self.validator.add_field_validators("name", lambda x: len(x) < 10)
        data = {"name": "VeryLongNameThatExceedsTenCharacters"}
        result = self.validator.validate(data)
        assert not result

    def test_remove_field_validators(self):
        """Test remove_field_validators method."""
        # Add validators to a field
        self.validator.add_validator("name", lambda x: isinstance(x, str))
        self.validator.add_validator("age", lambda x: isinstance(x, int))

        # Verify validators exist
        assert len(self.validator.get_field_validators("name")) > 0
        assert len(self.validator.get_field_validators("age")) > 0

        # Remove validators for name field
        self.validator.remove_field_validators("name")

        # Verify name validators are removed
        assert len(self.validator.get_field_validators("name")) == 0

        # Verify age validators still exist
        assert len(self.validator.get_field_validators("age")) > 0

        # Test removing non-existent field (should not raise error)
        self.validator.remove_field_validators("non_existent")

        # Test validation after removal
        data = {"name": "John", "age": 25}
        result = self.validator.validate(data)
        assert result  # Should pass because name has no validators

        data = {"name": "John", "age": "not_a_number"}
        result = self.validator.validate(data)
        assert not result  # Should fail because age validator still exists

    def test_get_field_validators(self):
        """Test get_field_validators method."""

        # Add validators to a field
        def validator1(x):
            return isinstance(x, str)

        def validator2(x):
            return len(x) > 0

        def validator3(x):
            return x.isalpha()

        self.validator.add_validator("name", validator1)
        self.validator.add_validator("name", validator2)
        self.validator.add_validator("name", validator3)

        # Get validators for the field
        validators = self.validator.get_field_validators("name")

        # Verify we got the right number of validators
        assert len(validators) == 3

        # Verify the validators are the same functions
        assert validators[0] == validator1
        assert validators[1] == validator2
        assert validators[2] == validator3

        # Test that modifying the returned list doesn't affect the original
        validators.append(lambda x: False)
        original_validators = self.validator.get_field_validators("name")
        assert len(original_validators) == 3  # Should still be 3

        # Test getting validators for non-existent field
        non_existent_validators = self.validator.get_field_validators("non_existent")
        assert len(non_existent_validators) == 0
        assert isinstance(non_existent_validators, list)

    def test_static_validator_methods(self):
        """Test static validator methods."""
        # Test required validator
        required_validator = DataValidator.required()
        assert required_validator("hello")
        assert required_validator(0)
        assert required_validator(False)
        assert not required_validator("")
        assert not required_validator(None)

        # Test min_length validator
        min_length_validator = DataValidator.min_length(3)
        assert min_length_validator("hello")
        assert min_length_validator([1, 2, 3, 4])  # "[1, 2, 3, 4]" has length 13
        assert not min_length_validator("hi")  # "hi" has length 2
        assert min_length_validator([1, 2])  # "[1, 2]" has length 5
        assert not min_length_validator([])  # "[]" has length 2

        # Test max_length validator
        max_length_validator = DataValidator.max_length(3)
        assert max_length_validator("hi")
        assert max_length_validator([1])  # "[1]" has length 3
        assert not max_length_validator([1, 2])  # "[1, 2]" has length 5
        assert not max_length_validator("hello")
        assert not max_length_validator([1, 2, 3, 4])

        # Test pattern validator
        pattern_validator = DataValidator.pattern(r"^\d+$")
        assert pattern_validator("123")
        assert pattern_validator("0")
        assert not pattern_validator("abc")
        assert not pattern_validator("123abc")

        # Test numeric_range validator
        range_validator = DataValidator.numeric_range(1, 10)
        assert range_validator(5)
        assert range_validator(1)
        assert range_validator(10)
        assert range_validator("5")  # "5" converts to 5.0
        assert not range_validator(0)
        assert not range_validator(11)
        # Non-numeric string should raise ValueError
        with pytest.raises(ValueError):
            range_validator("abc")

    def test_edge_cases(self):
        """Test various edge cases."""
        # Test with empty dict
        result = self.validator.validate({})
        assert result

        # Test with empty list
        result = self.validator.validate([])
        assert result

        # Test with None
        result = self.validator.validate(None)
        assert result

        # Test with complex nested structures
        data = {"nested": {"key": "value"}}
        result = self.validator.validate(data)
        assert result

    def test_protocol_compliance(self):
        """Test that DataValidator implements DataValidatorProtocol correctly."""
        # Verify it implements the protocol
        assert isinstance(self.validator, DataValidatorProtocol)

        # Test protocol methods exist
        assert hasattr(self.validator, "validate")
        assert hasattr(self.validator, "get_errors")
        assert hasattr(self.validator, "clear_errors")

        # Test method signatures
        assert callable(self.validator.validate)
        assert callable(self.validator.get_errors)
        assert callable(self.validator.clear_errors)


if __name__ == "__main__":
    unittest.main()
