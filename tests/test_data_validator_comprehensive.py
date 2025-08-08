"""
Comprehensive unit tests for DataValidator class to improve coverage.
"""

import unittest
from typing import Any, Dict, List

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
        self.assertTrue(result)
        self.assertEqual(len(self.validator.get_errors()), 0)
        
        # Test with non-string data (should fail)
        result = self.validator.validate(123)
        self.assertFalse(result)
        self.assertGreater(len(self.validator.get_errors()), 0)

    def test_validate_non_dict_list_data_without_validators(self):
        """Test validate method with non-dict/list data when no validators exist."""
        # No validators added
        result = self.validator.validate("hello")
        self.assertTrue(result)  # Should pass when no validators exist
        
        result = self.validator.validate(123)
        self.assertTrue(result)  # Should pass when no validators exist
        
        result = self.validator.validate(None)
        self.assertTrue(result)  # Should pass when no validators exist

    def test_validate_dict_with_missing_required_fields(self):
        """Test validate method with dictionary missing required fields."""
        self.validator.add_validator("name", lambda x: len(x) > 0)
        self.validator.add_validator("age", lambda x: isinstance(x, int) and x > 0)
        
        # Test with missing fields
        data = {"name": "John"}  # Missing age
        result = self.validator.validate(data)
        self.assertFalse(result)
        errors = self.validator.get_errors()
        self.assertIn("Field 'age' is required", errors)

    def test_validate_dict_with_invalid_values(self):
        """Test validate method with dictionary containing invalid values."""
        self.validator.add_validator("name", lambda x: len(x) > 0)
        self.validator.add_validator("age", lambda x: isinstance(x, int) and x > 0)
        
        # Test with invalid values
        data = {"name": "", "age": -5}  # Empty name, negative age
        result = self.validator.validate(data)
        self.assertFalse(result)
        errors = self.validator.get_errors()
        self.assertIn("Validation failed for field 'name'", errors)

    def test_validate_list_with_valid_indices(self):
        """Test validate method with list data using valid indices."""
        self.validator.add_validator("0", lambda x: isinstance(x, str))  # First element should be string
        self.validator.add_validator("1", lambda x: isinstance(x, int))  # Second element should be int
        
        # Test with valid list
        data = ["hello", 42]
        result = self.validator.validate(data)
        self.assertTrue(result)
        self.assertEqual(len(self.validator.get_errors()), 0)

    def test_validate_list_with_out_of_range_indices(self):
        """Test validate method with list data using out-of-range indices."""
        self.validator.add_validator("5", lambda x: True)  # Index 5 doesn't exist
        
        # Test with short list
        data = ["hello", "world"]
        result = self.validator.validate(data)
        self.assertFalse(result)
        errors = self.validator.get_errors()
        self.assertIn("Index 5 is out of range", errors)

    def test_validate_list_with_invalid_indices(self):
        """Test validate method with list data using invalid index names."""
        self.validator.add_validator("invalid", lambda x: True)  # Not a valid index
        
        # Test with list - should skip invalid indices
        data = ["hello", "world"]
        result = self.validator.validate(data)
        self.assertTrue(result)  # Should pass because invalid indices are skipped
        self.assertEqual(len(self.validator.get_errors()), 0)

    def test_validate_list_with_failing_validators(self):
        """Test validate method with list data where validators fail."""
        self.validator.add_validator("0", lambda x: isinstance(x, int))  # First element should be int
        self.validator.add_validator("1", lambda x: len(x) > 5)  # Second element should be long string
        
        # Test with failing validators
        data = ["hello", "short"]
        result = self.validator.validate(data)
        self.assertFalse(result)
        errors = self.validator.get_errors()
        self.assertIn("Validation failed for index 0", errors)

    def test_multiple_validators_per_field(self):
        """Test multiple validators per field."""
        self.validator.add_validator("name", lambda x: isinstance(x, str))
        self.validator.add_validator("name", lambda x: len(x) > 0)
        self.validator.add_validator("name", lambda x: x.isalpha())
        
        # Test with valid data
        data = {"name": "John"}
        result = self.validator.validate(data)
        self.assertTrue(result)
        
        # Test with invalid data (fails second validator)
        data = {"name": ""}
        result = self.validator.validate(data)
        self.assertFalse(result)
        
        # Test with invalid data (fails third validator)
        data = {"name": "John123"}
        result = self.validator.validate(data)
        self.assertFalse(result)

    def test_custom_validators(self):
        """Test custom validators functionality."""
        # Add a custom validator
        self.validator.add_custom_validator("email", lambda x: "@" in str(x))
        
        # Test that custom validators don't affect regular validation
        data = {"name": "John"}
        result = self.validator.validate(data)
        self.assertTrue(result)  # Should pass because no regular validators

    def test_clear_errors_functionality(self):
        """Test clear_errors method functionality."""
        # Add a validator and trigger an error
        self.validator.add_validator("name", lambda x: len(x) > 0)
        data = {"name": ""}
        result = self.validator.validate(data)
        self.assertFalse(result)
        self.assertGreater(len(self.validator.get_errors()), 0)
        
        # Clear errors
        self.validator.clear_errors()
        self.assertEqual(len(self.validator.get_errors()), 0)
        
        # Validate again - should work normally
        data = {"name": "John"}
        result = self.validator.validate(data)
        self.assertTrue(result)

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
        self.assertEqual(len(errors_again), original_length)
        self.assertNotIn("extra error", errors_again)

    def test_validate_detailed_method(self):
        """Test the validate_detailed method for backward compatibility."""
        self.validator.add_validator("name", lambda x: len(x) > 0)
        self.validator.add_validator("age", lambda x: isinstance(x, int))
        
        # Test with valid data
        data = {"name": "John", "age": 25}
        result = self.validator.validate_detailed(data)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)  # No errors
        
        # Test with invalid data
        data = {"name": "", "age": "not_a_number"}
        result = self.validator.validate_detailed(data)
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)  # Has errors

    def test_static_validator_methods(self):
        """Test static validator methods."""
        # Test required validator
        required_validator = DataValidator.required()
        self.assertTrue(required_validator("hello"))
        self.assertTrue(required_validator(0))
        self.assertTrue(required_validator(False))
        self.assertFalse(required_validator(""))
        self.assertFalse(required_validator(None))
        
        # Test min_length validator
        min_length_validator = DataValidator.min_length(3)
        self.assertTrue(min_length_validator("hello"))
        self.assertTrue(min_length_validator([1, 2, 3, 4]))  # "[1, 2, 3, 4]" has length 13
        self.assertFalse(min_length_validator("hi"))  # "hi" has length 2
        self.assertTrue(min_length_validator([1, 2]))  # "[1, 2]" has length 5
        self.assertFalse(min_length_validator([]))  # "[]" has length 2
        
        # Test max_length validator
        max_length_validator = DataValidator.max_length(3)
        self.assertTrue(max_length_validator("hi"))
        self.assertTrue(max_length_validator([1]))  # "[1]" has length 3
        self.assertFalse(max_length_validator([1, 2]))  # "[1, 2]" has length 5
        self.assertFalse(max_length_validator("hello"))
        self.assertFalse(max_length_validator([1, 2, 3, 4]))
        
        # Test pattern validator
        pattern_validator = DataValidator.pattern(r"^\d+$")
        self.assertTrue(pattern_validator("123"))
        self.assertTrue(pattern_validator("0"))
        self.assertFalse(pattern_validator("abc"))
        self.assertFalse(pattern_validator("123abc"))
        
        # Test numeric_range validator
        range_validator = DataValidator.numeric_range(1, 10)
        self.assertTrue(range_validator(5))
        self.assertTrue(range_validator(1))
        self.assertTrue(range_validator(10))
        self.assertTrue(range_validator("5"))  # "5" converts to 5.0
        self.assertFalse(range_validator(0))
        self.assertFalse(range_validator(11))
        # Non-numeric string should raise ValueError
        with self.assertRaises(ValueError):
            range_validator("abc")

    def test_edge_cases(self):
        """Test various edge cases."""
        # Test with empty dict
        result = self.validator.validate({})
        self.assertTrue(result)
        
        # Test with empty list
        result = self.validator.validate([])
        self.assertTrue(result)
        
        # Test with None
        result = self.validator.validate(None)
        self.assertTrue(result)
        
        # Test with complex nested structures
        data = {"nested": {"key": "value"}}
        result = self.validator.validate(data)
        self.assertTrue(result)

    def test_protocol_compliance(self):
        """Test that DataValidator implements DataValidatorProtocol correctly."""
        # Verify it implements the protocol
        self.assertIsInstance(self.validator, DataValidatorProtocol)
        
        # Test protocol methods exist
        self.assertTrue(hasattr(self.validator, 'validate'))
        self.assertTrue(hasattr(self.validator, 'get_errors'))
        self.assertTrue(hasattr(self.validator, 'clear_errors'))
        
        # Test method signatures
        self.assertTrue(callable(self.validator.validate))
        self.assertTrue(callable(self.validator.get_errors))
        self.assertTrue(callable(self.validator.clear_errors))


if __name__ == "__main__":
    unittest.main()
