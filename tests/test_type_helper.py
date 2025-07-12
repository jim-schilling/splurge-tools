"""
Unit tests for type_helper module
"""

import unittest
from datetime import date, datetime, time

from splurge_tools.type_helper import (
    DataType,
    String,
    is_dict_like,
    is_empty,
    is_iterable,
    is_iterable_not_string,
    is_list_like,
    profile_values,
)


class TestString(unittest.TestCase):
    """Test cases for String class methods"""

    def test_is_bool_like(self):
        """Test boolean-like value detection"""
        # Test boolean values
        self.assertTrue(String.is_bool_like(True))
        self.assertTrue(String.is_bool_like(False))

        # Test string values
        self.assertTrue(String.is_bool_like("true"))
        self.assertTrue(String.is_bool_like("false"))
        self.assertTrue(String.is_bool_like("TRUE"))
        self.assertTrue(String.is_bool_like("FALSE"))

        # Test with whitespace
        self.assertTrue(String.is_bool_like(" true "))
        self.assertTrue(String.is_bool_like(" false "))

        # Test non-boolean values
        self.assertFalse(String.is_bool_like("yes"))
        self.assertFalse(String.is_bool_like("no"))
        self.assertFalse(String.is_bool_like(None))
        self.assertFalse(String.is_bool_like(1))
        self.assertFalse(String.is_bool_like(0))

    def test_is_none_like(self):
        """Test None-like value detection"""
        # Test None values
        self.assertTrue(String.is_none_like(None))

        # Test string values
        self.assertTrue(String.is_none_like("none"))
        self.assertTrue(String.is_none_like("null"))
        self.assertTrue(String.is_none_like("NONE"))
        self.assertTrue(String.is_none_like("NULL"))

        # Test with whitespace
        self.assertTrue(String.is_none_like(" none "))
        self.assertTrue(String.is_none_like(" null "))

        # Test non-None values
        self.assertFalse(String.is_none_like(""))
        self.assertFalse(String.is_none_like("0"))
        self.assertFalse(String.is_none_like(0))
        self.assertFalse(String.is_none_like([]))

    def test_is_float_like(self):
        """Test float-like value detection"""
        # Test float values
        self.assertTrue(String.is_float_like(1.23))
        self.assertTrue(String.is_float_like(-1.23))

        # Test string values
        self.assertTrue(String.is_float_like("1.23"))
        self.assertTrue(String.is_float_like("-1.23"))
        self.assertTrue(String.is_float_like(".23"))
        self.assertTrue(String.is_float_like("1."))

        # Test with whitespace
        self.assertTrue(String.is_float_like(" 1.23 "))

        # Test non-float values
        self.assertFalse(String.is_float_like("1,23"))
        self.assertFalse(String.is_float_like("abc"))
        self.assertFalse(String.is_float_like(None))
        self.assertFalse(String.is_float_like([]))

    def test_is_int_like(self):
        """Test integer-like value detection"""
        # Test integer values
        self.assertTrue(String.is_int_like(123))
        self.assertTrue(String.is_int_like(-123))

        # Test string values
        self.assertTrue(String.is_int_like("123"))
        self.assertTrue(String.is_int_like("-123"))

        # Test with whitespace
        self.assertTrue(String.is_int_like(" 123 "))

        # Test non-integer values
        self.assertFalse(String.is_int_like("123.45"))
        self.assertFalse(String.is_int_like("abc"))
        self.assertFalse(String.is_int_like(None))
        self.assertFalse(String.is_int_like([]))

    def test_is_numeric_like(self):
        """Test numeric-like value detection"""
        # Test numeric values
        self.assertTrue(String.is_numeric_like(123))
        self.assertTrue(String.is_numeric_like(123.45))
        self.assertTrue(String.is_numeric_like(-123))
        self.assertTrue(String.is_numeric_like(-123.45))

        # Test string values
        self.assertTrue(String.is_numeric_like("123"))
        self.assertTrue(String.is_numeric_like("123.45"))
        self.assertTrue(String.is_numeric_like("-123"))
        self.assertTrue(String.is_numeric_like("-123.45"))

        # Test non-numeric values
        self.assertFalse(String.is_numeric_like("abc"))
        self.assertFalse(String.is_numeric_like(None))
        self.assertFalse(String.is_numeric_like([]))

    def test_is_date_like(self):
        """Test date-like value detection"""
        # Test date values
        test_date = date(2023, 1, 1)
        self.assertTrue(String.is_date_like(test_date))

        # Test string values
        self.assertTrue(String.is_date_like("2023-01-01"))
        self.assertTrue(String.is_date_like("2023/01/01"))
        self.assertTrue(String.is_date_like("01-01-2023"))
        self.assertTrue(String.is_date_like("01/01/2023"))

        # Test with whitespace
        self.assertTrue(String.is_date_like(" 2023-01-01 "))

        # Test non-date values
        self.assertFalse(String.is_date_like("2023-13-27"))  # Invalid month
        self.assertFalse(String.is_date_like("abc"))
        self.assertFalse(String.is_date_like(None))
        self.assertFalse(String.is_date_like([]))

    def test_is_datetime_like(self):
        """Test datetime-like value detection"""
        # Test datetime values
        test_datetime = datetime(2023, 1, 1, 12, 30, 45)
        self.assertTrue(String.is_datetime_like(test_datetime))

        # Test string values
        self.assertTrue(String.is_datetime_like("2023-01-01T12:30:45"))
        self.assertTrue(String.is_datetime_like("2023-01-01T12:30:45.12340"))
        self.assertTrue(String.is_datetime_like("2023/01/01T12:30:45"))

        # Test with whitespace
        self.assertTrue(String.is_datetime_like(" 2023-01-01T12:30:45 "))

        # Test non-datetime values
        self.assertFalse(
            String.is_datetime_like("2023-13-27T12:30:45")
        )  # Invalid month
        self.assertFalse(String.is_datetime_like("abc"))
        self.assertFalse(String.is_datetime_like(None))
        self.assertFalse(String.is_datetime_like([]))

    def test_to_bool(self):
        """Test boolean conversion"""
        # Test boolean values
        self.assertTrue(String.to_bool(True))
        self.assertFalse(String.to_bool(False))

        # Test string values
        self.assertTrue(String.to_bool("true"))
        self.assertFalse(String.to_bool("false"))

        # Test with default
        self.assertIsNone(String.to_bool("invalid", default=None))
        self.assertFalse(String.to_bool("invalid", default=False))

        # Test with whitespace
        self.assertTrue(String.to_bool(" true "))
        self.assertFalse(String.to_bool(" false "))

    def test_to_float(self):
        """Test float conversion"""
        # Test float values
        self.assertEqual(String.to_float(1.23), 1.23)
        self.assertEqual(String.to_float(-1.23), -1.23)

        # Test string values
        self.assertEqual(String.to_float("1.23"), 1.23)
        self.assertEqual(String.to_float("-1.23"), -1.23)

        # Test with default
        self.assertIsNone(String.to_float("invalid", default=None))
        self.assertEqual(String.to_float("invalid", default=0.0), 0.0)

        # Test with whitespace
        self.assertEqual(String.to_float(" 1.23 "), 1.23)

    def test_to_int(self):
        """Test integer conversion"""
        # Test integer values
        self.assertEqual(String.to_int(123), 123)
        self.assertEqual(String.to_int(-123), -123)

        # Test string values
        self.assertEqual(String.to_int("123"), 123)
        self.assertEqual(String.to_int("-123"), -123)

        # Test with default
        self.assertIsNone(String.to_int("invalid", default=None))
        self.assertEqual(String.to_int("invalid", default=0), 0)

        # Test with whitespace
        self.assertEqual(String.to_int(" 123 "), 123)

    def test_to_date(self):
        """Test date conversion"""
        # Test date values
        test_date = date(2023, 1, 1)
        self.assertEqual(String.to_date(test_date), test_date)

        # Test string values
        self.assertEqual(String.to_date("2023-01-01"), date(2023, 1, 1))
        self.assertEqual(String.to_date("2023/01/01"), date(2023, 1, 1))

        # Test with default
        self.assertIsNone(String.to_date("invalid", default=None))
        default_date = date(2023, 1, 1)
        self.assertEqual(String.to_date("invalid", default=default_date), default_date)

        # Test with whitespace
        self.assertEqual(String.to_date(" 2023-01-01 "), date(2023, 1, 1))

    def test_to_datetime(self):
        """Test datetime conversion"""
        # Test datetime values
        test_datetime = datetime(2023, 1, 1, 12, 30, 45)
        self.assertEqual(String.to_datetime(test_datetime), test_datetime)

        # Test string values
        self.assertEqual(
            String.to_datetime("2023-01-01T12:30:45"), datetime(2023, 1, 1, 12, 30, 45)
        )

        # Test with default
        self.assertIsNone(String.to_datetime("invalid", default=None))
        default_datetime = datetime(2023, 1, 1, 12, 30, 45)
        self.assertEqual(
            String.to_datetime("invalid", default=default_datetime), default_datetime
        )

        # Test with whitespace
        self.assertEqual(
            String.to_datetime(" 2023-01-01T12:30:45 "),
            datetime(2023, 1, 1, 12, 30, 45),
        )

    def test_has_leading_zero(self):
        """Test leading zero detection"""
        # Test with leading zero
        self.assertTrue(String.has_leading_zero("01"))
        self.assertTrue(String.has_leading_zero(" 01 "))

        # Test without leading zero
        self.assertFalse(String.has_leading_zero("1"))
        self.assertFalse(String.has_leading_zero("10"))
        self.assertFalse(String.has_leading_zero(None))
        self.assertFalse(String.has_leading_zero(""))

    def test_infer_type(self):
        """Test type inference"""
        # Test basic types
        self.assertEqual(String.infer_type(None), DataType.NONE)
        self.assertEqual(String.infer_type(True), DataType.BOOLEAN)
        self.assertEqual(String.infer_type(123), DataType.INTEGER)
        self.assertEqual(String.infer_type(123.45), DataType.FLOAT)
        self.assertEqual(String.infer_type("abc"), DataType.STRING)

        # Test date types
        self.assertEqual(String.infer_type(date(2023, 1, 1)), DataType.DATE)
        self.assertEqual(
            String.infer_type(datetime(2023, 1, 1, 12, 30, 45)), DataType.DATETIME
        )
        self.assertEqual(String.infer_type(time(14, 30, 45)), DataType.TIME)

        # Test string representations
        self.assertEqual(String.infer_type("2023-01-01"), DataType.DATE)
        self.assertEqual(String.infer_type("2023-01-01T12:30:45"), DataType.DATETIME)
        self.assertEqual(String.infer_type("14:30:45"), DataType.TIME)
        self.assertEqual(String.infer_type("2:30 PM"), DataType.TIME)
        self.assertEqual(String.infer_type("123"), DataType.INTEGER)
        self.assertEqual(String.infer_type("123.45"), DataType.FLOAT)
        self.assertEqual(String.infer_type("true"), DataType.BOOLEAN)

    def test_is_empty_like(self):
        """Test is_empty_like method."""
        # Test empty strings
        self.assertTrue(String.is_empty_like(""))
        self.assertTrue(String.is_empty_like("   "))
        self.assertTrue(String.is_empty_like("\t\n\r"))

        # Test non-empty strings
        self.assertFalse(String.is_empty_like("abc"))
        self.assertFalse(String.is_empty_like("  abc  "))

        # Test non-string values
        self.assertFalse(String.is_empty_like(None))
        self.assertFalse(String.is_empty_like(123))
        self.assertFalse(String.is_empty_like([]))
        self.assertFalse(String.is_empty_like({}))

        # Test with trim=False
        self.assertFalse(String.is_empty_like("   ", trim=False))
        self.assertTrue(String.is_empty_like("", trim=False))

    def test_is_time_like(self):
        """Test time-like value detection"""
        # Test time values
        test_time = time(14, 30, 45)
        self.assertTrue(String.is_time_like(test_time))

        # Test valid time strings - 24-hour format
        self.assertTrue(String.is_time_like("14:30:45"))
        self.assertTrue(String.is_time_like("14:30:45.123456"))
        self.assertTrue(String.is_time_like("14:30"))
        self.assertTrue(String.is_time_like("143045"))
        self.assertTrue(String.is_time_like("1430"))
        self.assertTrue(String.is_time_like("00:00:00"))  # Midnight
        self.assertTrue(String.is_time_like("23:59:59"))  # End of day
        self.assertTrue(String.is_time_like("12:00:00"))  # Noon

        # Test valid time strings - 12-hour format
        self.assertTrue(String.is_time_like("2:30 PM"))
        self.assertTrue(String.is_time_like("2:30:45 PM"))
        self.assertTrue(String.is_time_like("2:30PM"))
        self.assertTrue(String.is_time_like("2:30:45PM"))
        self.assertTrue(String.is_time_like("12:00 AM"))  # Midnight
        self.assertTrue(String.is_time_like("12:00 PM"))  # Noon
        self.assertTrue(String.is_time_like("11:59 PM"))  # End of day
        self.assertTrue(String.is_time_like("12:30 AM"))  # Early morning

        # Test with whitespace
        self.assertTrue(String.is_time_like(" 14:30:45 "))
        self.assertTrue(String.is_time_like(" 2:30 PM "))

        # Test invalid time values
        self.assertFalse(String.is_time_like("25:30:45"))  # Invalid hour
        self.assertFalse(String.is_time_like("14:60:45"))  # Invalid minute
        self.assertFalse(String.is_time_like("14:30:60"))  # Invalid second
        self.assertFalse(String.is_time_like("13:30 PM"))  # Invalid 13 PM
        self.assertFalse(String.is_time_like("0:30 AM"))   # Invalid 0 AM
        self.assertFalse(String.is_time_like("12:30:60 PM"))  # Invalid seconds
        self.assertFalse(String.is_time_like("abc"))
        self.assertFalse(String.is_time_like(None))
        self.assertFalse(String.is_time_like([]))
        self.assertFalse(String.is_time_like("2023-01-01"))  # Date, not time
        self.assertFalse(String.is_time_like("14:30:45:67"))  # Too many components
        self.assertFalse(String.is_time_like("14:30:45.123456789"))  # Too many microseconds

    def test_to_time(self):
        """Test time conversion"""
        # Test time values
        test_time = time(14, 30, 45)
        self.assertEqual(String.to_time(test_time), test_time)

        # Test valid time strings - 24-hour format
        self.assertEqual(
            String.to_time("14:30:45"), time(14, 30, 45)
        )
        self.assertEqual(
            String.to_time("14:30"), time(14, 30)
        )
        self.assertEqual(
            String.to_time("143045"), time(14, 30, 45)
        )
        self.assertEqual(
            String.to_time("1430"), time(14, 30)
        )
        self.assertEqual(
            String.to_time("00:00:00"), time(0, 0, 0)  # Midnight
        )
        self.assertEqual(
            String.to_time("23:59:59"), time(23, 59, 59)  # End of day
        )
        self.assertEqual(
            String.to_time("12:00:00"), time(12, 0, 0)  # Noon
        )

        # Test valid time strings - 12-hour format
        self.assertEqual(
            String.to_time("2:30 PM"), time(14, 30)
        )
        self.assertEqual(
            String.to_time("2:30:45 PM"), time(14, 30, 45)
        )
        self.assertEqual(
            String.to_time("12:00 AM"), time(0, 0, 0)  # Midnight
        )
        self.assertEqual(
            String.to_time("12:00 PM"), time(12, 0, 0)  # Noon
        )
        self.assertEqual(
            String.to_time("11:59 PM"), time(23, 59)  # End of day
        )
        self.assertEqual(
            String.to_time("12:30 AM"), time(0, 30)  # Early morning
        )

        # Test with microseconds
        self.assertEqual(
            String.to_time("14:30:45.123456"), time(14, 30, 45, 123456)
        )
        self.assertEqual(
            String.to_time("2:30:45.123456 PM"), time(14, 30, 45, 123456)
        )

        # Test with default
        self.assertIsNone(String.to_time("invalid", default=None))
        default_time = time(12, 0, 0)
        self.assertEqual(
            String.to_time("invalid", default=default_time), default_time
        )

        # Test with whitespace
        self.assertEqual(
            String.to_time(" 14:30:45 "),
            time(14, 30, 45),
        )
        self.assertEqual(
            String.to_time(" 2:30 PM "),
            time(14, 30),
        )

        # Test edge cases
        self.assertEqual(
            String.to_time("00:00"), time(0, 0)
        )
        self.assertEqual(
            String.to_time("23:59"), time(23, 59)
        )

    def test_time_type_inference(self):
        """Test time type inference and edge cases"""
        # Test time type inference
        self.assertEqual(String.infer_type(time(14, 30, 45)), DataType.TIME)
        self.assertEqual(String.infer_type("14:30:45"), DataType.TIME)
        self.assertEqual(String.infer_type("2:30 PM"), DataType.TIME)
        self.assertEqual(String.infer_type("143045"), DataType.TIME)
        
        # Test time type name inference
        self.assertEqual(String.infer_type_name(time(14, 30, 45)), "TIME")
        self.assertEqual(String.infer_type_name("14:30:45"), "TIME")
        self.assertEqual(String.infer_type_name("2:30 PM"), "TIME")
        
        # Test boundary conditions
        self.assertTrue(String.is_time_like("00:00:00"))  # Start of day
        self.assertTrue(String.is_time_like("23:59:59"))  # End of day
        self.assertTrue(String.is_time_like("12:00:00"))  # Noon
        self.assertTrue(String.is_time_like("12:00:00.000000"))  # Noon with microseconds
        
        # Test 12-hour format boundaries
        self.assertTrue(String.is_time_like("12:00 AM"))  # Midnight
        self.assertTrue(String.is_time_like("12:00 PM"))  # Noon
        self.assertTrue(String.is_time_like("11:59 PM"))  # End of day
        self.assertTrue(String.is_time_like("12:01 AM"))  # After midnight
        
        # Test invalid boundary conditions
        self.assertFalse(String.is_time_like("24:00:00"))  # Invalid hour
        self.assertFalse(String.is_time_like("23:60:00"))  # Invalid minute
        self.assertFalse(String.is_time_like("23:59:60"))  # Invalid second
        self.assertFalse(String.is_time_like("13:00 PM"))  # Invalid 13 PM
        self.assertFalse(String.is_time_like("0:00 AM"))   # Invalid 0 AM
        
        # Test conversion edge cases
        self.assertEqual(String.to_time("00:00:00.000000"), time(0, 0, 0, 0))
        self.assertEqual(String.to_time("23:59:59.999999"), time(23, 59, 59, 999999))
        
        # Test with trim=False
        self.assertFalse(String.is_time_like(" 14:30:45 ", trim=False))
        self.assertFalse(String.is_time_like(" 2:30 PM ", trim=False))


class TestProfileValues(unittest.TestCase):
    """Test cases for profile_values function"""

    def test_profile_values(self):
        """Test profile_values function."""
        # Test empty collections
        self.assertEqual(profile_values([]), DataType.EMPTY)

        # Test empty strings
        self.assertEqual(profile_values(["", "   ", "\t"]), DataType.EMPTY)

        # Test None values
        self.assertEqual(profile_values([None, None]), DataType.NONE)

        # Test mixed None and empty
        self.assertEqual(profile_values([None, "", "   "]), DataType.NONE)

        # Test boolean values
        self.assertEqual(profile_values(["true", "false"]), DataType.BOOLEAN)
        self.assertEqual(profile_values(["true", "false", ""]), DataType.BOOLEAN)

        # Test date values
        self.assertEqual(profile_values(["2023-01-01", "2023-01-02"]), DataType.DATE)
        self.assertEqual(
            profile_values(["2023-01-01", "2023-01-02", ""]), DataType.DATE
        )

        # Test datetime values
        self.assertEqual(
            profile_values(["2023-01-01T12:00:00", "2023-01-02T12:00:00"]),
            DataType.DATETIME,
        )
        self.assertEqual(
            profile_values(["2023-01-01T12:00:00", "2023-01-02T12:00:00", ""]),
            DataType.DATETIME,
        )

        # Test time values
        self.assertEqual(
            profile_values(["14:30:00", "15:45:00"]),
            DataType.TIME,
        )
        self.assertEqual(
            profile_values(["14:30:00", "15:45:00", ""]),
            DataType.TIME,
        )
        self.assertEqual(
            profile_values(["2:30 PM", "3:45 PM"]),
            DataType.TIME,
        )
        self.assertEqual(
            profile_values(["143000", "154500"]),
            DataType.TIME,
        )
        self.assertEqual(
            profile_values(["00:00:00", "23:59:59"]),
            DataType.TIME,
        )
        self.assertEqual(
            profile_values(["12:00 AM", "12:00 PM"]),
            DataType.TIME,
        )

        # Test integer values
        self.assertEqual(profile_values(["1", "2", "3"]), DataType.INTEGER)
        self.assertEqual(profile_values(["1", "2", "3", ""]), DataType.INTEGER)

        # Test float values
        self.assertEqual(profile_values(["1.1", "2.2", "3.3"]), DataType.FLOAT)
        self.assertEqual(profile_values(["1.1", "2.2", "3.3", ""]), DataType.FLOAT)
        self.assertEqual(
            profile_values(["1", "2.2", "3"]), DataType.FLOAT
        )  # Mixed int and float

        # Test string values
        self.assertEqual(profile_values(["abc", "def"]), DataType.STRING)
        self.assertEqual(profile_values(["abc", "def", ""]), DataType.STRING)

        # Test mixed types
        self.assertEqual(profile_values(["1", "2.2", "abc"]), DataType.MIXED)
        self.assertEqual(profile_values(["1", "2.2", "abc", ""]), DataType.MIXED)

        # Test invalid input
        with self.assertRaises(ValueError):
            profile_values("not iterable")

        # Test with trim=False
        self.assertEqual(
            profile_values(["  true  ", "  false  "], trim=False), DataType.STRING
        )
        self.assertEqual(
            profile_values(["  1  ", "  2  "], trim=False), DataType.STRING
        )

    def test_profile_values_all_digit_edge_case(self):
        """Test edge case where all-digit strings could be interpreted as multiple types."""
        # Test case where all-digit strings could be interpreted as DATE, TIME, DATETIME, or INTEGER
        # Should prioritize INTEGER when all values are all-digit strings
        
        # Test all-digit strings that could be dates (YYYYMMDD format)
        self.assertEqual(profile_values(["20230101", "20230102", "20230103"]), DataType.DATE)
        
        # Test all-digit strings that could be times (HHMMSS format)
        self.assertEqual(profile_values(["143000", "154500", "120000"]), DataType.TIME)
        
        # Test all-digit strings that could be datetimes (YYYYMMDDHHMMSS format)
        self.assertEqual(profile_values(["20230101143000", "20230102154500"]), DataType.DATETIME)
        
        # Test mixed all-digit strings with different interpretations
        self.assertEqual(profile_values(["20230101", "143000", "12345"]), DataType.INTEGER)
        
        # Test with negative numbers
        self.assertEqual(profile_values(["-20230101", "-143000", "-12345"]), DataType.INTEGER)
        
        # Test with positive signs
        self.assertEqual(profile_values(["+20230101", "+143000", "+12345"]), DataType.INTEGER)
        
        # Test mixed positive and negative
        self.assertEqual(profile_values(["+20230101", "-143000", "12345"]), DataType.INTEGER)
        
        # Test that non-all-digit strings still result in MIXED when appropriate
        self.assertEqual(profile_values(["20230101", "143000", "abc"]), DataType.MIXED)
        self.assertEqual(profile_values(["20230101", "143000", "1.23"]), DataType.MIXED)
        
        # Test that regular date/time formats still work correctly
        self.assertEqual(profile_values(["2023-01-01", "2023-01-02"]), DataType.DATE)
        self.assertEqual(profile_values(["14:30:00", "15:45:00"]), DataType.TIME)
        self.assertEqual(profile_values(["2023-01-01T14:30:00", "2023-01-02T15:45:00"]), DataType.DATETIME)

    def test_profile_values_pure_vs_mixed_sequences(self):
        """Test that pure sequences are classified correctly while mixed sequences prioritize INTEGER."""
        # Test pure sequences (should be classified as their actual type)
        self.assertEqual(profile_values(["20230101", "20230102", "20230103"]), DataType.DATE)
        self.assertEqual(profile_values(["143000", "154500", "120000"]), DataType.TIME)
        self.assertEqual(profile_values(["20230101143000", "20230102154500"]), DataType.DATETIME)
        self.assertEqual(profile_values(["123", "456", "789"]), DataType.INTEGER)
        
        # Test mixed sequences (should prioritize INTEGER)
        self.assertEqual(profile_values(["20230101", "143000", "12345"]), DataType.INTEGER)
        self.assertEqual(profile_values(["20230101", "12345", "143000"]), DataType.INTEGER)
        self.assertEqual(profile_values(["143000", "20230101", "12345"]), DataType.INTEGER)
        self.assertEqual(profile_values(["20230101143000", "12345", "20230101"]), DataType.INTEGER)
        
        # Test edge cases with empty values
        self.assertEqual(profile_values(["20230101", "143000", ""]), DataType.INTEGER)
        self.assertEqual(profile_values(["20230101", "", "143000"]), DataType.INTEGER)
        
        # Test INTEGER + EMPTY (should be INTEGER)
        self.assertEqual(profile_values(["123", "456", ""]), DataType.INTEGER)
        self.assertEqual(profile_values(["123", "", "456"]), DataType.INTEGER)
        
        # Test that non-all-digit strings still result in MIXED
        self.assertEqual(profile_values(["20230101", "143000", "abc"]), DataType.MIXED)
        self.assertEqual(profile_values(["20230101", "143000", "1.23"]), DataType.MIXED)
        
        # Test with generators (non-reusable iterators)
        def gen_values():
            yield "20230101"
            yield "143000"
            yield "12345"
        
        self.assertEqual(profile_values(gen_values()), DataType.INTEGER)
        
        # Test with tuples (reusable sequences)
        self.assertEqual(profile_values(("20230101", "143000", "12345")), DataType.INTEGER)
        
        # Test generator with pure integer values
        def gen_integers():
            yield "123"
            yield "456"
            yield "789"
        
        self.assertEqual(profile_values(gen_integers()), DataType.INTEGER)
        
        # Test generator with mixed types
        def gen_mixed():
            yield "123"
            yield "abc"
            yield "456"
        
        self.assertEqual(profile_values(gen_mixed()), DataType.MIXED)




class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions"""

    def test_is_list_like(self):
        """Test list-like detection"""
        # Test list types
        self.assertTrue(is_list_like([]))
        self.assertTrue(is_list_like([1, 2, 3]))

        # Test non-list types
        self.assertFalse(is_list_like({}))
        self.assertFalse(is_list_like("abc"))
        self.assertFalse(is_list_like(None))
        self.assertFalse(is_list_like(123))

    def test_is_dict_like(self):
        """Test dict-like detection"""
        # Test dict types
        self.assertTrue(is_dict_like({}))
        self.assertTrue(is_dict_like({"a": 1}))

        # Test non-dict types
        self.assertFalse(is_dict_like([]))
        self.assertFalse(is_dict_like("abc"))
        self.assertFalse(is_dict_like(None))
        self.assertFalse(is_dict_like(123))

    def test_is_iterable(self):
        """Test iterable detection"""
        # Test iterable types
        self.assertTrue(is_iterable([]))
        self.assertTrue(is_iterable({}))
        self.assertTrue(is_iterable("abc"))
        self.assertTrue(is_iterable((1, 2, 3)))

        # Test non-iterable types
        self.assertFalse(is_iterable(None))
        self.assertFalse(is_iterable(123))
        self.assertFalse(is_iterable(True))

    def test_is_iterable_not_string(self):
        """Test non-string iterable detection"""
        # Test non-string iterables
        self.assertTrue(is_iterable_not_string([]))
        self.assertTrue(is_iterable_not_string({}))
        self.assertTrue(is_iterable_not_string((1, 2, 3)))

        # Test strings and non-iterables
        self.assertFalse(is_iterable_not_string("abc"))
        self.assertFalse(is_iterable_not_string(None))
        self.assertFalse(is_iterable_not_string(123))

    def test_is_empty(self):
        """Test empty value detection"""
        # Test empty values
        self.assertTrue(is_empty(None))
        self.assertTrue(is_empty(""))
        self.assertTrue(is_empty(" "))
        self.assertTrue(is_empty([]))
        self.assertTrue(is_empty({}))
        self.assertTrue(is_empty(()))

        # Test non-empty values
        self.assertFalse(is_empty("abc"))
        self.assertFalse(is_empty([1, 2, 3]))
        self.assertFalse(is_empty({"a": 1}))
        self.assertFalse(is_empty(0))
        self.assertFalse(is_empty(False))


if __name__ == "__main__":
    unittest.main()
