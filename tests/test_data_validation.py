"""
Tests for data validation utilities.
"""

import unittest

from splurge_tools.data_validator import DataValidator


class TestDataValidator(unittest.TestCase):
    def setUp(self):
        self.validator = DataValidator()

    def test_required_validator(self):
        # Test required field validation
        self.validator.add_validator("name", DataValidator.required())

        # Valid data
        data = {"name": "John"}
        is_valid = self.validator.validate(data)
        self.assertTrue(is_valid)
        self.assertEqual(len(self.validator.get_errors()), 0)

        # Invalid data - missing field
        data = {}
        is_valid = self.validator.validate(data)
        self.assertFalse(is_valid)
        errors = self.validator.get_errors()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Field 'name' is required" in error for error in errors))

        # Invalid data - empty value
        data = {"name": ""}
        is_valid = self.validator.validate(data)
        self.assertFalse(is_valid)
        errors = self.validator.get_errors()
        self.assertGreater(len(errors), 0)

    def test_length_validators(self):
        # Test min and max length validation
        self.validator.add_validator("username", DataValidator.min_length(3))
        self.validator.add_validator("username", DataValidator.max_length(10))

        # Valid data
        data = {"username": "john_doe"}
        is_valid = self.validator.validate(data)
        self.assertTrue(is_valid)
        self.assertEqual(len(self.validator.get_errors()), 0)

        # Invalid data - too short
        data = {"username": "jo"}
        is_valid = self.validator.validate(data)
        self.assertFalse(is_valid)
        errors = self.validator.get_errors()
        self.assertGreater(len(errors), 0)

        # Invalid data - too long
        data = {"username": "john_doe_smith"}
        is_valid = self.validator.validate(data)
        self.assertFalse(is_valid)
        errors = self.validator.get_errors()
        self.assertGreater(len(errors), 0)

    def test_pattern_validator(self):
        # Test pattern validation
        self.validator.add_validator(
            "phone", DataValidator.pattern(r"^\d{3}-\d{3}-\d{4}$")
        )

        # Valid data
        data = {"phone": "123-456-7890"}
        is_valid = self.validator.validate(data)
        self.assertTrue(is_valid)
        self.assertEqual(len(self.validator.get_errors()), 0)

        # Invalid data
        data = {"phone": "1234567890"}
        is_valid = self.validator.validate(data)
        self.assertFalse(is_valid)
        errors = self.validator.get_errors()
        self.assertGreater(len(errors), 0)

    def test_range_validator(self):
        # Test range validation
        self.validator.add_validator("age", DataValidator.numeric_range(0, 120))

        # Valid data
        data = {"age": 25}
        is_valid = self.validator.validate(data)
        self.assertTrue(is_valid)
        self.assertEqual(len(self.validator.get_errors()), 0)

        # Invalid data
        data = {"age": 150}
        is_valid = self.validator.validate(data)
        self.assertFalse(is_valid)
        errors = self.validator.get_errors()
        self.assertGreater(len(errors), 0)

    def test_protocol_compliance(self):
        """Test that DataValidator properly implements DataValidatorProtocol."""
        from splurge_tools.protocols import DataValidatorProtocol
        
        # Test that it implements the protocol
        self.assertIsInstance(self.validator, DataValidatorProtocol)
        
        # Test protocol methods exist
        self.assertTrue(hasattr(self.validator, 'validate'))
        self.assertTrue(hasattr(self.validator, 'get_errors'))
        self.assertTrue(hasattr(self.validator, 'clear_errors'))
        
        # Test method signatures
        self.assertTrue(callable(self.validator.validate))
        self.assertTrue(callable(self.validator.get_errors))
        self.assertTrue(callable(self.validator.clear_errors))

    def test_clear_errors(self):
        """Test that clear_errors works correctly."""
        self.validator.add_validator("name", DataValidator.required())
        
        # Create some errors
        data = {}
        self.validator.validate(data)
        self.assertGreater(len(self.validator.get_errors()), 0)
        
        # Clear errors
        self.validator.clear_errors()
        self.assertEqual(len(self.validator.get_errors()), 0)

    def test_validate_detailed_method(self):
        """Test the validate_detailed method for backward compatibility."""
        self.validator.add_validator("name", DataValidator.required())
        
        # Valid data
        data = {"name": "John"}
        errors = self.validator.validate_detailed(data)
        self.assertEqual(len(errors), 0)
        
        # Invalid data
        data = {}
        errors = self.validator.validate_detailed(data)
        self.assertIn("name", errors)
        self.assertIn("Field is required", errors["name"])


if __name__ == "__main__":
    unittest.main()
