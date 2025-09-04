"""
Unit tests for TypeInference class and TypeInferenceProtocol compliance.
"""

import unittest
from datetime import date, datetime, time

from splurge_tools.protocols import TypeInferenceProtocol
from splurge_tools.type_helper import DataType, TypeInference


class TestTypeInference(unittest.TestCase):
    """Test cases for TypeInference class"""

    def setUp(self):
        """Set up test fixtures"""
        self.type_inference = TypeInference()

    def test_protocol_compliance(self):
        """Test that TypeInference implements TypeInferenceProtocol"""
        # Verify it implements the protocol
        assert isinstance(self.type_inference, TypeInferenceProtocol)

        # Test protocol methods exist
        assert hasattr(self.type_inference, "can_infer")
        assert hasattr(self.type_inference, "infer_type")
        assert hasattr(self.type_inference, "convert_value")

        # Test method signatures
        assert callable(self.type_inference.can_infer)
        assert callable(self.type_inference.infer_type)
        assert callable(self.type_inference.convert_value)

    def test_can_infer_method(self):
        """Test the can_infer method"""
        # Test values that can be inferred as specific types
        assert self.type_inference.can_infer("123")
        assert self.type_inference.can_infer("-456")
        assert self.type_inference.can_infer("3.14")
        assert self.type_inference.can_infer("-2.5")
        assert self.type_inference.can_infer("true")
        assert self.type_inference.can_infer("false")
        assert self.type_inference.can_infer("2023-01-15")
        assert self.type_inference.can_infer("14:30:00")
        assert self.type_inference.can_infer("2023-01-15T14:30:00")
        assert self.type_inference.can_infer("none")
        assert self.type_inference.can_infer("")

        # Test values that remain as strings
        assert not self.type_inference.can_infer("hello")
        assert not self.type_inference.can_infer("abc123")
        assert not self.type_inference.can_infer("123abc")

        # Test non-string inputs
        assert not self.type_inference.can_infer(123)
        assert not self.type_inference.can_infer(3.14)
        assert not self.type_inference.can_infer(True)
        assert not self.type_inference.can_infer(None)

    def test_infer_type_method(self):
        """Test the infer_type method"""
        # Test integer inference
        assert self.type_inference.infer_type("123") == DataType.INTEGER
        assert self.type_inference.infer_type("-456") == DataType.INTEGER
        assert self.type_inference.infer_type("0") == DataType.INTEGER

        # Test float inference
        assert self.type_inference.infer_type("3.14") == DataType.FLOAT
        assert self.type_inference.infer_type("-2.5") == DataType.FLOAT
        assert self.type_inference.infer_type(".5") == DataType.FLOAT
        assert self.type_inference.infer_type("1.") == DataType.FLOAT

        # Test boolean inference
        assert self.type_inference.infer_type("true") == DataType.BOOLEAN
        assert self.type_inference.infer_type("false") == DataType.BOOLEAN
        assert self.type_inference.infer_type("TRUE") == DataType.BOOLEAN
        assert self.type_inference.infer_type("FALSE") == DataType.BOOLEAN

        # Test date inference
        assert self.type_inference.infer_type("2023-01-15") == DataType.DATE
        assert self.type_inference.infer_type("2023/01/15") == DataType.DATE
        assert self.type_inference.infer_type("2023.01.15") == DataType.DATE

        # Test time inference
        assert self.type_inference.infer_type("14:30:00") == DataType.TIME
        assert self.type_inference.infer_type("2:30 PM") == DataType.TIME
        assert self.type_inference.infer_type("143000") == DataType.TIME

        # Test datetime inference
        assert self.type_inference.infer_type("2023-01-15T14:30:00") == DataType.DATETIME
        # Note: Microseconds format "2023-01-15T14:30:00.123" is not currently supported

        # Test special cases
        assert self.type_inference.infer_type("none") == DataType.NONE
        assert self.type_inference.infer_type("null") == DataType.NONE
        assert self.type_inference.infer_type("") == DataType.EMPTY
        assert self.type_inference.infer_type("   ") == DataType.EMPTY

        # Test string inference (fallback)
        assert self.type_inference.infer_type("hello") == DataType.STRING
        assert self.type_inference.infer_type("abc123") == DataType.STRING
        assert self.type_inference.infer_type("123abc") == DataType.STRING

    def test_convert_value_method(self):
        """Test the convert_value method"""
        # Test integer conversion
        assert self.type_inference.convert_value("123") == 123
        assert self.type_inference.convert_value("-456") == -456
        assert self.type_inference.convert_value("0") == 0

        # Test float conversion
        assert self.type_inference.convert_value("3.14") == 3.14
        assert self.type_inference.convert_value("-2.5") == -2.5
        assert self.type_inference.convert_value(".5") == 0.5
        assert self.type_inference.convert_value("1.") == 1.0

        # Test boolean conversion
        assert self.type_inference.convert_value("true")
        assert not self.type_inference.convert_value("false")
        assert self.type_inference.convert_value("TRUE")
        assert not self.type_inference.convert_value("FALSE")

        # Test date conversion
        expected_date = date(2023, 1, 15)
        assert self.type_inference.convert_value("2023-01-15") == expected_date

        # Test time conversion
        expected_time = time(14, 30)
        assert self.type_inference.convert_value("14:30:00") == expected_time

        # Test datetime conversion
        expected_datetime = datetime(2023, 1, 15, 14, 30)
        assert self.type_inference.convert_value("2023-01-15T14:30:00") == expected_datetime

        # Test special cases
        assert self.type_inference.convert_value("none") is None
        assert self.type_inference.convert_value("null") is None
        assert self.type_inference.convert_value("") == ""
        assert self.type_inference.convert_value("   ") == ""

        # Test string conversion (fallback)
        assert self.type_inference.convert_value("hello") == "hello"
        assert self.type_inference.convert_value("abc123") == "abc123"
        assert self.type_inference.convert_value("123abc") == "123abc"

    def test_integration_workflow(self):
        """Test the complete workflow: can_infer -> infer_type -> convert_value"""
        test_cases = [
            ("123", True, DataType.INTEGER, 123),
            ("3.14", True, DataType.FLOAT, 3.14),
            ("true", True, DataType.BOOLEAN, True),
            ("2023-01-15", True, DataType.DATE, date(2023, 1, 15)),
            ("14:30:00", True, DataType.TIME, time(14, 30)),
            ("2023-01-15T14:30:00", True, DataType.DATETIME, datetime(2023, 1, 15, 14, 30)),
            ("none", True, DataType.NONE, None),
            ("", True, DataType.EMPTY, ""),
            ("hello", False, DataType.STRING, "hello"),
        ]

        for value, can_infer, expected_type, expected_converted in test_cases:
            with self.subTest(value=value):
                # Test can_infer
                assert self.type_inference.can_infer(value) == can_infer

                # Test infer_type
                assert self.type_inference.infer_type(value) == expected_type

                # Test convert_value
                assert self.type_inference.convert_value(value) == expected_converted

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test very large numbers
        assert self.type_inference.can_infer("999999999999999999")
        assert self.type_inference.infer_type("999999999999999999") == DataType.INTEGER

        # Test very small numbers
        assert self.type_inference.can_infer("0.0000000001")
        assert self.type_inference.infer_type("0.0000000001") == DataType.FLOAT

        # Test whitespace handling
        assert self.type_inference.can_infer("  123  ")
        assert self.type_inference.infer_type("  123  ") == DataType.INTEGER
        assert self.type_inference.convert_value("  123  ") == 123

        # Test empty and whitespace-only strings
        assert self.type_inference.can_infer("")
        assert self.type_inference.can_infer("   ")
        assert self.type_inference.infer_type("") == DataType.EMPTY
        assert self.type_inference.infer_type("   ") == DataType.EMPTY
        assert self.type_inference.convert_value("") == ""
        assert self.type_inference.convert_value("   ") == ""

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with None (should not raise exception)
        assert not self.type_inference.can_infer(None)

        # Test with non-string types (should not raise exception)
        assert not self.type_inference.can_infer(123)
        assert not self.type_inference.can_infer(3.14)
        assert not self.type_inference.can_infer(True)
        assert not self.type_inference.can_infer([])
        assert not self.type_inference.can_infer({})

    def test_multiple_instances(self):
        """Test that multiple instances work independently"""
        instance1 = TypeInference()
        instance2 = TypeInference()

        # Both instances should work identically
        assert instance1.can_infer("123") == instance2.can_infer("123")
        assert instance1.infer_type("123") == instance2.infer_type("123")
        assert instance1.convert_value("123") == instance2.convert_value("123")


if __name__ == "__main__":
    unittest.main()
