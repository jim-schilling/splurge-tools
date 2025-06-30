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
        errors = self.validator.validate(data)
        self.assertEqual(len(errors), 0)

        # Invalid data - missing field
        data = {}
        errors = self.validator.validate(data)
        self.assertIn("name", errors)
        self.assertIn("Field is required", errors["name"])

        # Invalid data - empty value
        data = {"name": ""}
        errors = self.validator.validate(data)
        self.assertIn("name", errors)

    def test_length_validators(self):
        # Test min and max length validation
        self.validator.add_validator("username", DataValidator.min_length(3))
        self.validator.add_validator("username", DataValidator.max_length(10))

        # Valid data
        data = {"username": "john_doe"}
        errors = self.validator.validate(data)
        self.assertEqual(len(errors), 0)

        # Invalid data - too short
        data = {"username": "jo"}
        errors = self.validator.validate(data)
        self.assertIn("username", errors)

        # Invalid data - too long
        data = {"username": "john_doe_smith"}
        errors = self.validator.validate(data)
        self.assertIn("username", errors)

    def test_pattern_validator(self):
        # Test pattern validation
        self.validator.add_validator(
            "phone", DataValidator.pattern(r"^\d{3}-\d{3}-\d{4}$")
        )

        # Valid data
        data = {"phone": "123-456-7890"}
        errors = self.validator.validate(data)
        self.assertEqual(len(errors), 0)

        # Invalid data
        data = {"phone": "1234567890"}
        errors = self.validator.validate(data)
        self.assertIn("phone", errors)

    def test_range_validator(self):
        # Test range validation
        self.validator.add_validator("age", DataValidator.numeric_range(0, 120))

        # Valid data
        data = {"age": 25}
        errors = self.validator.validate(data)
        self.assertEqual(len(errors), 0)

        # Invalid data
        data = {"age": 150}
        errors = self.validator.validate(data)
        self.assertIn("age", errors)


if __name__ == "__main__":
    unittest.main()
