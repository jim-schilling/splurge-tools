"""
Unit tests for TypeInference class and TypeInferenceProtocol compliance.
"""

import unittest
from datetime import date, datetime, time

from splurge_tools.type_helper import TypeInference, DataType
from splurge_tools.protocols import TypeInferenceProtocol


class TestTypeInference(unittest.TestCase):
    """Test cases for TypeInference class"""

    def setUp(self):
        """Set up test fixtures"""
        self.type_inference = TypeInference()

    def test_protocol_compliance(self):
        """Test that TypeInference implements TypeInferenceProtocol"""
        # Verify it implements the protocol
        self.assertIsInstance(self.type_inference, TypeInferenceProtocol)
        
        # Test protocol methods exist
        self.assertTrue(hasattr(self.type_inference, 'can_infer'))
        self.assertTrue(hasattr(self.type_inference, 'infer_type'))
        self.assertTrue(hasattr(self.type_inference, 'convert_value'))
        
        # Test method signatures
        self.assertTrue(callable(self.type_inference.can_infer))
        self.assertTrue(callable(self.type_inference.infer_type))
        self.assertTrue(callable(self.type_inference.convert_value))

    def test_can_infer_method(self):
        """Test the can_infer method"""
        # Test values that can be inferred as specific types
        self.assertTrue(self.type_inference.can_infer("123"))
        self.assertTrue(self.type_inference.can_infer("-456"))
        self.assertTrue(self.type_inference.can_infer("3.14"))
        self.assertTrue(self.type_inference.can_infer("-2.5"))
        self.assertTrue(self.type_inference.can_infer("true"))
        self.assertTrue(self.type_inference.can_infer("false"))
        self.assertTrue(self.type_inference.can_infer("2023-01-15"))
        self.assertTrue(self.type_inference.can_infer("14:30:00"))
        self.assertTrue(self.type_inference.can_infer("2023-01-15T14:30:00"))
        self.assertTrue(self.type_inference.can_infer("none"))
        self.assertTrue(self.type_inference.can_infer(""))
        
        # Test values that remain as strings
        self.assertFalse(self.type_inference.can_infer("hello"))
        self.assertFalse(self.type_inference.can_infer("abc123"))
        self.assertFalse(self.type_inference.can_infer("123abc"))
        
        # Test non-string inputs
        self.assertFalse(self.type_inference.can_infer(123))
        self.assertFalse(self.type_inference.can_infer(3.14))
        self.assertFalse(self.type_inference.can_infer(True))
        self.assertFalse(self.type_inference.can_infer(None))

    def test_infer_type_method(self):
        """Test the infer_type method"""
        # Test integer inference
        self.assertEqual(self.type_inference.infer_type("123"), DataType.INTEGER)
        self.assertEqual(self.type_inference.infer_type("-456"), DataType.INTEGER)
        self.assertEqual(self.type_inference.infer_type("0"), DataType.INTEGER)
        
        # Test float inference
        self.assertEqual(self.type_inference.infer_type("3.14"), DataType.FLOAT)
        self.assertEqual(self.type_inference.infer_type("-2.5"), DataType.FLOAT)
        self.assertEqual(self.type_inference.infer_type(".5"), DataType.FLOAT)
        self.assertEqual(self.type_inference.infer_type("1."), DataType.FLOAT)
        
        # Test boolean inference
        self.assertEqual(self.type_inference.infer_type("true"), DataType.BOOLEAN)
        self.assertEqual(self.type_inference.infer_type("false"), DataType.BOOLEAN)
        self.assertEqual(self.type_inference.infer_type("TRUE"), DataType.BOOLEAN)
        self.assertEqual(self.type_inference.infer_type("FALSE"), DataType.BOOLEAN)
        
        # Test date inference
        self.assertEqual(self.type_inference.infer_type("2023-01-15"), DataType.DATE)
        self.assertEqual(self.type_inference.infer_type("2023/01/15"), DataType.DATE)
        self.assertEqual(self.type_inference.infer_type("2023.01.15"), DataType.DATE)
        
        # Test time inference
        self.assertEqual(self.type_inference.infer_type("14:30:00"), DataType.TIME)
        self.assertEqual(self.type_inference.infer_type("2:30 PM"), DataType.TIME)
        self.assertEqual(self.type_inference.infer_type("143000"), DataType.TIME)
        
        # Test datetime inference
        self.assertEqual(self.type_inference.infer_type("2023-01-15T14:30:00"), DataType.DATETIME)
        # Note: Microseconds format "2023-01-15T14:30:00.123" is not currently supported
        
        # Test special cases
        self.assertEqual(self.type_inference.infer_type("none"), DataType.NONE)
        self.assertEqual(self.type_inference.infer_type("null"), DataType.NONE)
        self.assertEqual(self.type_inference.infer_type(""), DataType.EMPTY)
        self.assertEqual(self.type_inference.infer_type("   "), DataType.EMPTY)
        
        # Test string inference (fallback)
        self.assertEqual(self.type_inference.infer_type("hello"), DataType.STRING)
        self.assertEqual(self.type_inference.infer_type("abc123"), DataType.STRING)
        self.assertEqual(self.type_inference.infer_type("123abc"), DataType.STRING)

    def test_convert_value_method(self):
        """Test the convert_value method"""
        # Test integer conversion
        self.assertEqual(self.type_inference.convert_value("123"), 123)
        self.assertEqual(self.type_inference.convert_value("-456"), -456)
        self.assertEqual(self.type_inference.convert_value("0"), 0)
        
        # Test float conversion
        self.assertEqual(self.type_inference.convert_value("3.14"), 3.14)
        self.assertEqual(self.type_inference.convert_value("-2.5"), -2.5)
        self.assertEqual(self.type_inference.convert_value(".5"), 0.5)
        self.assertEqual(self.type_inference.convert_value("1."), 1.0)
        
        # Test boolean conversion
        self.assertEqual(self.type_inference.convert_value("true"), True)
        self.assertEqual(self.type_inference.convert_value("false"), False)
        self.assertEqual(self.type_inference.convert_value("TRUE"), True)
        self.assertEqual(self.type_inference.convert_value("FALSE"), False)
        
        # Test date conversion
        expected_date = date(2023, 1, 15)
        self.assertEqual(self.type_inference.convert_value("2023-01-15"), expected_date)
        
        # Test time conversion
        expected_time = time(14, 30)
        self.assertEqual(self.type_inference.convert_value("14:30:00"), expected_time)
        
        # Test datetime conversion
        expected_datetime = datetime(2023, 1, 15, 14, 30)
        self.assertEqual(self.type_inference.convert_value("2023-01-15T14:30:00"), expected_datetime)
        
        # Test special cases
        self.assertIsNone(self.type_inference.convert_value("none"))
        self.assertIsNone(self.type_inference.convert_value("null"))
        self.assertEqual(self.type_inference.convert_value(""), "")
        self.assertEqual(self.type_inference.convert_value("   "), "")
        
        # Test string conversion (fallback)
        self.assertEqual(self.type_inference.convert_value("hello"), "hello")
        self.assertEqual(self.type_inference.convert_value("abc123"), "abc123")
        self.assertEqual(self.type_inference.convert_value("123abc"), "123abc")

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
                self.assertEqual(self.type_inference.can_infer(value), can_infer)
                
                # Test infer_type
                self.assertEqual(self.type_inference.infer_type(value), expected_type)
                
                # Test convert_value
                self.assertEqual(self.type_inference.convert_value(value), expected_converted)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test very large numbers
        self.assertTrue(self.type_inference.can_infer("999999999999999999"))
        self.assertEqual(self.type_inference.infer_type("999999999999999999"), DataType.INTEGER)
        
        # Test very small numbers
        self.assertTrue(self.type_inference.can_infer("0.0000000001"))
        self.assertEqual(self.type_inference.infer_type("0.0000000001"), DataType.FLOAT)
        
        # Test whitespace handling
        self.assertTrue(self.type_inference.can_infer("  123  "))
        self.assertEqual(self.type_inference.infer_type("  123  "), DataType.INTEGER)
        self.assertEqual(self.type_inference.convert_value("  123  "), 123)
        
        # Test empty and whitespace-only strings
        self.assertTrue(self.type_inference.can_infer(""))
        self.assertTrue(self.type_inference.can_infer("   "))
        self.assertEqual(self.type_inference.infer_type(""), DataType.EMPTY)
        self.assertEqual(self.type_inference.infer_type("   "), DataType.EMPTY)
        self.assertEqual(self.type_inference.convert_value(""), "")
        self.assertEqual(self.type_inference.convert_value("   "), "")

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with None (should not raise exception)
        self.assertFalse(self.type_inference.can_infer(None))
        
        # Test with non-string types (should not raise exception)
        self.assertFalse(self.type_inference.can_infer(123))
        self.assertFalse(self.type_inference.can_infer(3.14))
        self.assertFalse(self.type_inference.can_infer(True))
        self.assertFalse(self.type_inference.can_infer([]))
        self.assertFalse(self.type_inference.can_infer({}))

    def test_multiple_instances(self):
        """Test that multiple instances work independently"""
        instance1 = TypeInference()
        instance2 = TypeInference()
        
        # Both instances should work identically
        self.assertEqual(instance1.can_infer("123"), instance2.can_infer("123"))
        self.assertEqual(instance1.infer_type("123"), instance2.infer_type("123"))
        self.assertEqual(instance1.convert_value("123"), instance2.convert_value("123"))


if __name__ == "__main__":
    unittest.main()
