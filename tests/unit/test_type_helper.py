"""
Unit tests for type_helper module
"""

from datetime import date, datetime, time

import pytest

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


class TestString:
    """Test cases for String class methods"""

    def test_is_bool_like(self):
        """Test boolean-like value detection"""
        # Test boolean values
        assert String.is_bool_like(True)
        assert String.is_bool_like(False)

        # Test string values
        assert String.is_bool_like("true")
        assert String.is_bool_like("false")
        assert String.is_bool_like("TRUE")
        assert String.is_bool_like("FALSE")

        # Test with whitespace
        assert String.is_bool_like(" true ")
        assert String.is_bool_like(" false ")

        # Test non-boolean values
        assert not String.is_bool_like("yes")
        assert not String.is_bool_like("no")
        assert not String.is_bool_like(None)
        assert not String.is_bool_like(1)
        assert not String.is_bool_like(0)

    def test_is_none_like(self):
        """Test None-like value detection"""
        # Test None values
        assert String.is_none_like(None)

        # Test string values
        assert String.is_none_like("none")
        assert String.is_none_like("null")
        assert String.is_none_like("NONE")
        assert String.is_none_like("NULL")

        # Test with whitespace
        assert String.is_none_like(" none ")
        assert String.is_none_like(" null ")

        # Test non-None values
        assert not String.is_none_like("")
        assert not String.is_none_like("0")
        assert not String.is_none_like(0)
        assert not String.is_none_like([])

    def test_is_float_like(self):
        """Test float-like value detection"""
        # Test float values
        assert String.is_float_like(1.23)
        assert String.is_float_like(-1.23)

        # Test string values
        assert String.is_float_like("1.23")
        assert String.is_float_like("-1.23")
        assert String.is_float_like(".23")
        assert String.is_float_like("1.")

        # Test with whitespace
        assert String.is_float_like(" 1.23 ")

        # Test non-float values
        assert not String.is_float_like("1,23")
        assert not String.is_float_like("abc")
        assert not String.is_float_like(None)
        assert not String.is_float_like([])

    def test_is_int_like(self):
        """Test integer-like value detection"""
        # Test integer values
        assert String.is_int_like(123)
        assert String.is_int_like(-123)

        # Test string values
        assert String.is_int_like("123")
        assert String.is_int_like("-123")

        # Test with whitespace
        assert String.is_int_like(" 123 ")

        # Test non-integer values
        assert not String.is_int_like("123.45")
        assert not String.is_int_like("abc")
        assert not String.is_int_like(None)
        assert not String.is_int_like([])

    def test_is_numeric_like(self):
        """Test numeric-like value detection"""
        # Test numeric values
        assert String.is_numeric_like(123)
        assert String.is_numeric_like(123.45)
        assert String.is_numeric_like(-123)
        assert String.is_numeric_like(-123.45)

        # Test string values
        assert String.is_numeric_like("123")
        assert String.is_numeric_like("123.45")
        assert String.is_numeric_like("-123")
        assert String.is_numeric_like("-123.45")

        # Test non-numeric values
        assert not String.is_numeric_like("abc")
        assert not String.is_numeric_like(None)
        assert not String.is_numeric_like([])

    def test_is_date_like(self):
        """Test date-like value detection"""
        # Test date values
        test_date = date(2023, 1, 1)
        assert String.is_date_like(test_date)

        # Test string values
        assert String.is_date_like("2023-01-01")
        assert String.is_date_like("2023/01/01")
        assert String.is_date_like("01-01-2023")
        assert String.is_date_like("01/01/2023")

        # Test with whitespace
        assert String.is_date_like(" 2023-01-01 ")

        # Test non-date values
        assert not String.is_date_like("2023-13-27")  # Invalid month
        assert not String.is_date_like("abc")
        assert not String.is_date_like(None)
        assert not String.is_date_like([])

    def test_is_datetime_like(self):
        """Test datetime-like value detection"""
        # Test datetime values
        test_datetime = datetime(2023, 1, 1, 12, 30, 45)
        assert String.is_datetime_like(test_datetime)

        # Test string values
        assert String.is_datetime_like("2023-01-01T12:30:45")
        assert String.is_datetime_like("2023-01-01T12:30:45.12340")
        assert String.is_datetime_like("2023/01/01T12:30:45")

        # Test with whitespace
        assert String.is_datetime_like(" 2023-01-01T12:30:45 ")

        # Test non-datetime values
        assert not String.is_datetime_like("2023-13-27T12:30:45")  # Invalid month
        assert not String.is_datetime_like("abc")
        assert not String.is_datetime_like(None)
        assert not String.is_datetime_like([])

    def test_to_bool(self):
        """Test boolean conversion"""
        # Test boolean values
        assert String.to_bool(True)
        assert not String.to_bool(False)

        # Test string values
        assert String.to_bool("true")
        assert not String.to_bool("false")

        # Test with default
        assert String.to_bool("invalid", default=None) is None
        assert not String.to_bool("invalid", default=False)

        # Test with whitespace
        assert String.to_bool(" true ")
        assert not String.to_bool(" false ")

    def test_to_float(self):
        """Test float conversion"""
        # Test float values
        assert String.to_float(1.23) == 1.23
        assert String.to_float(-1.23) == -1.23

        # Test string values
        assert String.to_float("1.23") == 1.23
        assert String.to_float("-1.23") == -1.23

        # Test with default
        assert String.to_float("invalid", default=None) is None
        assert String.to_float("invalid", default=0.0) == 0.0

        # Test with whitespace
        assert String.to_float(" 1.23 ") == 1.23

    def test_to_int(self):
        """Test integer conversion"""
        # Test integer values
        assert String.to_int(123) == 123
        assert String.to_int(-123) == -123

        # Test string values
        assert String.to_int("123") == 123
        assert String.to_int("-123") == -123

        # Test with default
        assert String.to_int("invalid", default=None) is None
        assert String.to_int("invalid", default=0) == 0

        # Test with whitespace
        assert String.to_int(" 123 ") == 123

    def test_to_date(self):
        """Test date conversion"""
        # Test date values
        test_date = date(2023, 1, 1)
        assert String.to_date(test_date) == test_date

        # Test string values
        assert String.to_date("2023-01-01") == date(2023, 1, 1)
        assert String.to_date("2023/01/01") == date(2023, 1, 1)

        # Test with default
        assert String.to_date("invalid", default=None) is None
        default_date = date(2023, 1, 1)
        assert String.to_date("invalid", default=default_date) == default_date

        # Test with whitespace
        assert String.to_date(" 2023-01-01 ") == date(2023, 1, 1)

    def test_to_datetime(self):
        """Test datetime conversion"""
        # Test datetime values
        test_datetime = datetime(2023, 1, 1, 12, 30, 45)
        assert String.to_datetime(test_datetime) == test_datetime

        # Test string values
        assert String.to_datetime("2023-01-01T12:30:45") == datetime(2023, 1, 1, 12, 30, 45)

        # Test with default
        assert String.to_datetime("invalid", default=None) is None
        default_datetime = datetime(2023, 1, 1, 12, 30, 45)
        assert String.to_datetime("invalid", default=default_datetime) == default_datetime

        # Test with whitespace
        assert String.to_datetime(" 2023-01-01T12:30:45 ") == datetime(2023, 1, 1, 12, 30, 45)

    def test_has_leading_zero(self):
        """Test leading zero detection"""
        # Test with leading zero
        assert String.has_leading_zero("01")
        assert String.has_leading_zero(" 01 ")

        # Test without leading zero
        assert not String.has_leading_zero("1")
        assert not String.has_leading_zero("10")
        assert not String.has_leading_zero(None)
        assert not String.has_leading_zero("")

    def test_infer_type(self):
        """Test type inference"""
        # Test basic types
        assert String.infer_type(None) == DataType.NONE
        assert String.infer_type(True) == DataType.BOOLEAN
        assert String.infer_type(123) == DataType.INTEGER
        assert String.infer_type(123.45) == DataType.FLOAT
        assert String.infer_type("abc") == DataType.STRING

        # Test date types
        assert String.infer_type(date(2023, 1, 1)) == DataType.DATE
        assert String.infer_type(datetime(2023, 1, 1, 12, 30, 45)) == DataType.DATETIME
        assert String.infer_type(time(14, 30, 45)) == DataType.TIME

        # Test string representations
        assert String.infer_type("2023-01-01") == DataType.DATE
        assert String.infer_type("2023-01-01T12:30:45") == DataType.DATETIME
        assert String.infer_type("14:30:45") == DataType.TIME
        assert String.infer_type("2:30 PM") == DataType.TIME
        assert String.infer_type("123") == DataType.INTEGER
        assert String.infer_type("123.45") == DataType.FLOAT
        assert String.infer_type("true") == DataType.BOOLEAN

    def test_is_empty_like(self):
        """Test is_empty_like method."""
        # Test empty strings
        assert String.is_empty_like("")
        assert String.is_empty_like("   ")
        assert String.is_empty_like("\t\n\r")

        # Test non-empty strings
        assert not String.is_empty_like("abc")
        assert not String.is_empty_like("  abc  ")

        # Test non-string values
        assert not String.is_empty_like(None)
        assert not String.is_empty_like(123)
        assert not String.is_empty_like([])
        assert not String.is_empty_like({})

        # Test with trim=False
        assert not String.is_empty_like("   ", trim=False)
        assert String.is_empty_like("", trim=False)

    def test_is_time_like(self):
        """Test time-like value detection"""
        # Test time values
        test_time = time(14, 30, 45)
        assert String.is_time_like(test_time)

        # Test valid time strings - 24-hour format
        assert String.is_time_like("14:30:45")
        assert String.is_time_like("14:30:45.123456")
        assert String.is_time_like("14:30")
        assert String.is_time_like("143045")
        assert String.is_time_like("1430")
        assert String.is_time_like("00:00:00")  # Midnight
        assert String.is_time_like("23:59:59")  # End of day
        assert String.is_time_like("12:00:00")  # Noon

        # Test valid time strings - 12-hour format
        assert String.is_time_like("2:30 PM")
        assert String.is_time_like("2:30:45 PM")
        assert String.is_time_like("2:30PM")
        assert String.is_time_like("2:30:45PM")
        assert String.is_time_like("12:00 AM")  # Midnight
        assert String.is_time_like("12:00 PM")  # Noon
        assert String.is_time_like("11:59 PM")  # End of day
        assert String.is_time_like("12:30 AM")  # Early morning

        # Test with whitespace
        assert String.is_time_like(" 14:30:45 ")
        assert String.is_time_like(" 2:30 PM ")

        # Test invalid time values
        assert not String.is_time_like("25:30:45")  # Invalid hour
        assert not String.is_time_like("14:60:45")  # Invalid minute
        assert not String.is_time_like("14:30:60")  # Invalid second
        assert not String.is_time_like("13:30 PM")  # Invalid 13 PM
        assert not String.is_time_like("0:30 AM")  # Invalid 0 AM
        assert not String.is_time_like("12:30:60 PM")  # Invalid seconds
        assert not String.is_time_like("abc")
        assert not String.is_time_like(None)
        assert not String.is_time_like([])
        assert not String.is_time_like("2023-01-01")  # Date, not time
        assert not String.is_time_like("14:30:45:67")  # Too many components
        assert not String.is_time_like("14:30:45.123456789")  # Too many microseconds

    def test_to_time(self):
        """Test time conversion"""
        # Test time values
        test_time = time(14, 30, 45)
        assert String.to_time(test_time) == test_time

        # Test valid time strings - 24-hour format
        assert String.to_time("14:30:45") == time(14, 30, 45)
        assert String.to_time("14:30") == time(14, 30)
        assert String.to_time("143045") == time(14, 30, 45)
        assert String.to_time("1430") == time(14, 30)
        assert String.to_time("00:00:00") == time(0, 0, 0)
        assert String.to_time("23:59:59") == time(23, 59, 59)
        assert String.to_time("12:00:00") == time(12, 0, 0)

        # Test valid time strings - 12-hour format
        assert String.to_time("2:30 PM") == time(14, 30)
        assert String.to_time("2:30:45 PM") == time(14, 30, 45)
        assert String.to_time("12:00 AM") == time(0, 0, 0)
        assert String.to_time("12:00 PM") == time(12, 0, 0)
        assert String.to_time("11:59 PM") == time(23, 59)
        assert String.to_time("12:30 AM") == time(0, 30)

        # Test with microseconds
        assert String.to_time("14:30:45.123456") == time(14, 30, 45, 123456)
        assert String.to_time("2:30:45.123456 PM") == time(14, 30, 45, 123456)

        # Test with default
        assert String.to_time("invalid", default=None) is None
        default_time = time(12, 0, 0)
        assert String.to_time("invalid", default=default_time) == default_time

        # Test with whitespace
        assert String.to_time(" 14:30:45 ") == time(14, 30, 45)
        assert String.to_time(" 2:30 PM ") == time(14, 30)

        # Test edge cases
        assert String.to_time("00:00") == time(0, 0)
        assert String.to_time("23:59") == time(23, 59)

    def test_time_type_inference(self):
        """Test time type inference and edge cases"""
        # Test time type inference
        assert String.infer_type(time(14, 30, 45)) == DataType.TIME
        assert String.infer_type("14:30:45") == DataType.TIME
        assert String.infer_type("2:30 PM") == DataType.TIME
        assert String.infer_type("143045") == DataType.TIME

        # Test time type name inference
        assert String.infer_type_name(time(14, 30, 45)) == "TIME"
        assert String.infer_type_name("14:30:45") == "TIME"
        assert String.infer_type_name("2:30 PM") == "TIME"

        # Test boundary conditions
        assert String.is_time_like("00:00:00")  # Start of day
        assert String.is_time_like("23:59:59")  # End of day
        assert String.is_time_like("12:00:00")  # Noon
        assert String.is_time_like("12:00:00.000000")  # Noon with microseconds

        # Test 12-hour format boundaries
        assert String.is_time_like("12:00 AM")  # Midnight
        assert String.is_time_like("12:00 PM")  # Noon
        assert String.is_time_like("11:59 PM")  # End of day
        assert String.is_time_like("12:01 AM")  # After midnight

        # Test invalid boundary conditions
        assert not String.is_time_like("24:00:00")  # Invalid hour
        assert not String.is_time_like("23:60:00")  # Invalid minute
        assert not String.is_time_like("23:59:60")  # Invalid second
        assert not String.is_time_like("13:00 PM")  # Invalid 13 PM
        assert not String.is_time_like("0:00 AM")  # Invalid 0 AM

        # Test conversion edge cases
        assert String.to_time("00:00:00.000000") == time(0, 0, 0, 0)
        assert String.to_time("23:59:59.999999") == time(23, 59, 59, 999999)

        # Test with trim=False
        assert not String.is_time_like(" 14:30:45 ", trim=False)
        assert not String.is_time_like(" 2:30 PM ", trim=False)


class TestProfileValues:
    """Test cases for profile_values function"""

    def test_profile_values(self):
        """Test profile_values function."""
        # Test empty collections
        assert profile_values([]) == DataType.EMPTY

        # Test empty strings
        assert profile_values(["", "   ", "\t"]) == DataType.EMPTY

        # Test None values
        assert profile_values([None, None]) == DataType.NONE

        # Test mixed None and empty
        assert profile_values([None, "", "   "]) == DataType.NONE

        # Test boolean values
        assert profile_values(["true", "false"]) == DataType.BOOLEAN
        assert profile_values(["true", "false", ""]) == DataType.BOOLEAN

        # Test date values
        assert profile_values(["2023-01-01", "2023-01-02"]) == DataType.DATE
        assert profile_values(["2023-01-01", "2023-01-02", ""]) == DataType.DATE

        # Test datetime values
        assert profile_values(["2023-01-01T12:00:00", "2023-01-02T12:00:00"]) == DataType.DATETIME
        assert profile_values(["2023-01-01T12:00:00", "2023-01-02T12:00:00", ""]) == DataType.DATETIME

        # Test time values
        assert profile_values(["14:30:00", "15:45:00"]) == DataType.TIME
        assert profile_values(["14:30:00", "15:45:00", ""]) == DataType.TIME
        assert profile_values(["2:30 PM", "3:45 PM"]) == DataType.TIME
        assert profile_values(["143000", "154500"]) == DataType.TIME
        assert profile_values(["00:00:00", "23:59:59"]) == DataType.TIME
        assert profile_values(["12:00 AM", "12:00 PM"]) == DataType.TIME

        # Test integer values
        assert profile_values(["1", "2", "3"]) == DataType.INTEGER
        assert profile_values(["1", "2", "3", ""]) == DataType.INTEGER

        # Test float values
        assert profile_values(["1.1", "2.2", "3.3"]) == DataType.FLOAT
        assert profile_values(["1.1", "2.2", "3.3", ""]) == DataType.FLOAT
        assert profile_values(["1", "2.2", "3"]) == DataType.FLOAT  # Mixed int and float

        # Test string values
        assert profile_values(["abc", "def"]) == DataType.STRING
        assert profile_values(["abc", "def", ""]) == DataType.STRING

        # Test mixed types
        assert profile_values(["1", "2.2", "abc"]) == DataType.MIXED
        assert profile_values(["1", "2.2", "abc", ""]) == DataType.MIXED

        # Test invalid input
        with pytest.raises(ValueError):
            profile_values("not iterable")

        # Test with trim=False
        assert profile_values(["  true  ", "  false  "], trim=False) == DataType.STRING
        assert profile_values(["  1  ", "  2  "], trim=False) == DataType.STRING

    def test_profile_values_all_digit_edge_case(self):
        """Test edge case where all-digit strings could be interpreted as multiple types."""
        # Test case where all-digit strings could be interpreted as DATE, TIME, DATETIME, or INTEGER
        # Should prioritize INTEGER when all values are all-digit strings

        # Test all-digit strings that could be dates (YYYYMMDD format)
        assert profile_values(["20230101", "20230102", "20230103"]) == DataType.DATE

        # Test all-digit strings that could be times (HHMMSS format)
        assert profile_values(["143000", "154500", "120000"]) == DataType.TIME

        # Test all-digit strings that could be datetimes (YYYYMMDDHHMMSS format)
        assert profile_values(["20230101143000", "20230102154500"]) == DataType.DATETIME

        # Test mixed all-digit strings with different interpretations
        assert profile_values(["20230101", "143000", "12345"]) == DataType.INTEGER

        # Test with negative numbers
        assert profile_values(["-20230101", "-143000", "-12345"]) == DataType.INTEGER

        # Test with positive signs
        assert profile_values(["+20230101", "+143000", "+12345"]) == DataType.INTEGER

        # Test mixed positive and negative
        assert profile_values(["+20230101", "-143000", "12345"]) == DataType.INTEGER

        # Test that non-all-digit strings still result in MIXED when appropriate
        assert profile_values(["20230101", "143000", "abc"]) == DataType.MIXED
        assert profile_values(["20230101", "143000", "1.23"]) == DataType.MIXED

        # Test that regular date/time formats still work correctly
        assert profile_values(["2023-01-01", "2023-01-02"]) == DataType.DATE
        assert profile_values(["14:30:00", "15:45:00"]) == DataType.TIME
        assert profile_values(["2023-01-01T14:30:00", "2023-01-02T15:45:00"]) == DataType.DATETIME

    def test_profile_values_pure_vs_mixed_sequences(self):
        """Test that pure sequences are classified correctly while mixed sequences prioritize INTEGER."""
        # Test pure sequences (should be classified as their actual type)
        assert profile_values(["20230101", "20230102", "20230103"]) == DataType.DATE
        assert profile_values(["143000", "154500", "120000"]) == DataType.TIME
        assert profile_values(["20230101143000", "20230102154500"]) == DataType.DATETIME
        assert profile_values(["123", "456", "789"]) == DataType.INTEGER

        # Test mixed sequences (should prioritize INTEGER)
        assert profile_values(["20230101", "143000", "12345"]) == DataType.INTEGER
        assert profile_values(["20230101", "12345", "143000"]) == DataType.INTEGER
        assert profile_values(["143000", "20230101", "12345"]) == DataType.INTEGER
        assert profile_values(["20230101143000", "12345", "20230101"]) == DataType.INTEGER

        # Test edge cases with empty values
        assert profile_values(["20230101", "143000", ""]) == DataType.INTEGER
        assert profile_values(["20230101", "", "143000"]) == DataType.INTEGER

        # Test INTEGER + EMPTY (should be INTEGER)
        assert profile_values(["123", "456", ""]) == DataType.INTEGER
        assert profile_values(["123", "", "456"]) == DataType.INTEGER

        # Test that non-all-digit strings still result in MIXED
        assert profile_values(["20230101", "143000", "abc"]) == DataType.MIXED
        assert profile_values(["20230101", "143000", "1.23"]) == DataType.MIXED

        # Test with generators (non-reusable iterators)
        def gen_values():
            yield "20230101"
            yield "143000"
            yield "12345"

        assert profile_values(gen_values()) == DataType.INTEGER

        # Test with tuples (reusable sequences)
        assert profile_values(("20230101", "143000", "12345")) == DataType.INTEGER

        # Test generator with pure integer values
        def gen_integers():
            yield "123"
            yield "456"
            yield "789"

        assert profile_values(gen_integers()) == DataType.INTEGER

        # Test generator with mixed types
        def gen_mixed():
            yield "123"
            yield "abc"
            yield "456"

        assert profile_values(gen_mixed()) == DataType.MIXED

    @pytest.mark.parametrize(
        "values,expected_type",
        [
            ([], DataType.EMPTY),
            (["", "   ", "\t"], DataType.EMPTY),
            ([None, None], DataType.NONE),
            ([None, "", "   "], DataType.NONE),
            (["true", "false"], DataType.BOOLEAN),
            (["true", "false", ""], DataType.BOOLEAN),
            (["abc", "def"], DataType.STRING),
            (["abc", "def", ""], DataType.STRING),
            (["1", "2.2", "abc"], DataType.MIXED),
            (["1", "2.2", "abc", ""], DataType.MIXED),
            (["1", "2.2", "3"], DataType.FLOAT),
            (["20230101", "143000", "12345"], DataType.INTEGER),
            (["2023-01-01", "2023-01-02"], DataType.DATE),
            (["14:30:00", "15:45:00"], DataType.TIME),
            (["2023-01-01T12:00:00", "2023-01-02T12:00:00"], DataType.DATETIME),
        ],
        ids=[
            "row_0",
            "row_1",
            "row_2",
            "row_3",
            "row_4",
            "row_5",
            "row_6",
            "row_7",
            "row_8",
            "row_9",
            "row_10",
            "row_11",
            "row_12",
            "row_13",
            "row_14",
        ],
    )
    def test_profile_values_incremental_typecheck_flag(self, values, expected_type):
        """Test the use_incremental_typecheck flag functionality."""
        result_with_flag = profile_values(values, use_incremental_typecheck=True)
        result_without_flag = profile_values(values, use_incremental_typecheck=False)
        assert result_with_flag == expected_type
        assert result_without_flag == expected_type
        assert result_with_flag == result_without_flag

        # Test cases where incremental checking might make a difference
        # These are edge cases where the flag could potentially affect behavior

        # Test with large datasets where early termination could occur
        large_boolean_data = ["true"] * 100 + ["false"] * 100
        assert profile_values(large_boolean_data, use_incremental_typecheck=True) == DataType.BOOLEAN
        assert profile_values(large_boolean_data, use_incremental_typecheck=False) == DataType.BOOLEAN

        # Test with large string datasets
        large_string_data = ["abc"] * 100 + ["def"] * 100
        assert profile_values(large_string_data, use_incremental_typecheck=True) == DataType.STRING
        assert profile_values(large_string_data, use_incremental_typecheck=False) == DataType.STRING

        # Test with large empty datasets
        large_empty_data = [""] * 200
        assert profile_values(large_empty_data, use_incremental_typecheck=True) == DataType.EMPTY
        assert profile_values(large_empty_data, use_incremental_typecheck=False) == DataType.EMPTY
        result_with_flag = profile_values(values, use_incremental_typecheck=True)
        result_without_flag = profile_values(values, use_incremental_typecheck=False)
        assert result_with_flag == expected_type
        assert result_without_flag == expected_type
        assert result_with_flag == result_without_flag

        # Test with generators (non-reusable iterators)
        def gen_boolean():
            yield "true"
            yield "false"
            yield "true"

        assert profile_values(gen_boolean(), use_incremental_typecheck=True) == DataType.BOOLEAN
        assert profile_values(gen_boolean(), use_incremental_typecheck=False) == DataType.BOOLEAN

        # Test with tuples (reusable sequences)
        tuple_data = ("true", "false", "true")
        assert profile_values(tuple_data, use_incremental_typecheck=True) == DataType.BOOLEAN
        assert profile_values(tuple_data, use_incremental_typecheck=False) == DataType.BOOLEAN

        # Test with trim=False to ensure flag works with other parameters
        assert profile_values(["  true  ", "  false  "], trim=False, use_incremental_typecheck=True) == DataType.STRING
        assert profile_values(["  true  ", "  false  "], trim=False, use_incremental_typecheck=False) == DataType.STRING

        # Test that the flag parameter is properly handled
        # This ensures the parameter is actually being used and not ignored
        # We can't easily test the internal behavior, but we can verify the API works
        try:
            profile_values(["test"], use_incremental_typecheck=True)
            profile_values(["test"], use_incremental_typecheck=False)
        except Exception as e:
            pytest.fail(f"use_incremental_typecheck flag caused an error: {e}")

    def test_profile_values_early_mixed_detection(self):
        """Test early detection of MIXED type when both numeric/temporal and string types are present."""
        # Test cases where we should detect MIXED early (at 25% check point)

        # Integer + String (should detect MIXED early)
        mixed_int_string = [
            "123",
            "abc",
            "456",
            "def",
            "789",
            "ghi",
            "012",
            "jkl",
            "345",
            "mno",
            "678",
            "pqr",
        ]
        assert profile_values(mixed_int_string, use_incremental_typecheck=True) == DataType.MIXED
        assert profile_values(mixed_int_string, use_incremental_typecheck=False) == DataType.MIXED

        # Float + String (should detect MIXED early)
        mixed_float_string = [
            "1.23",
            "abc",
            "4.56",
            "def",
            "7.89",
            "ghi",
            "0.12",
            "jkl",
            "3.45",
            "mno",
            "6.78",
            "pqr",
        ]
        assert profile_values(mixed_float_string, use_incremental_typecheck=True) == DataType.MIXED
        assert profile_values(mixed_float_string, use_incremental_typecheck=False) == DataType.MIXED

        # Date + String (should detect MIXED early)
        mixed_date_string = [
            "2023-01-01",
            "abc",
            "2023-01-02",
            "def",
            "2023-01-03",
            "ghi",
            "2023-01-04",
            "jkl",
        ]
        assert profile_values(mixed_date_string, use_incremental_typecheck=True) == DataType.MIXED
        assert profile_values(mixed_date_string, use_incremental_typecheck=False) == DataType.MIXED

        # Time + String (should detect MIXED early)
        mixed_time_string = [
            "14:30:00",
            "abc",
            "15:45:00",
            "def",
            "16:00:00",
            "ghi",
            "17:15:00",
            "jkl",
        ]
        assert profile_values(mixed_time_string, use_incremental_typecheck=True) == DataType.MIXED
        assert profile_values(mixed_time_string, use_incremental_typecheck=False) == DataType.MIXED

        # Datetime + String (should detect MIXED early)
        mixed_datetime_string = [
            "2023-01-01T14:30:00",
            "abc",
            "2023-01-02T15:45:00",
            "def",
        ]
        assert profile_values(mixed_datetime_string, use_incremental_typecheck=True) == DataType.MIXED
        assert profile_values(mixed_datetime_string, use_incremental_typecheck=False) == DataType.MIXED

        # Multiple numeric types + String (should detect MIXED early)
        mixed_numeric_string = [
            "123",
            "1.23",
            "abc",
            "456",
            "4.56",
            "def",
            "789",
            "7.89",
            "ghi",
        ]
        assert profile_values(mixed_numeric_string, use_incremental_typecheck=True) == DataType.MIXED
        assert profile_values(mixed_numeric_string, use_incremental_typecheck=False) == DataType.MIXED

        # Test that pure types still work correctly (should NOT detect MIXED early)
        pure_integer = [
            "123",
            "456",
            "789",
            "012",
            "345",
            "678",
            "901",
            "234",
            "567",
            "890",
            "123",
            "456",
        ]
        assert profile_values(pure_integer, use_incremental_typecheck=True) == DataType.INTEGER
        assert profile_values(pure_integer, use_incremental_typecheck=False) == DataType.INTEGER

        pure_string = [
            "abc",
            "def",
            "ghi",
            "jkl",
            "mno",
            "pqr",
            "stu",
            "vwx",
            "yz",
            "ab",
            "cd",
            "ef",
        ]
        assert profile_values(pure_string, use_incremental_typecheck=True) == DataType.STRING
        assert profile_values(pure_string, use_incremental_typecheck=False) == DataType.STRING

        # Test with empty values (should still detect MIXED early)
        mixed_with_empty = ["123", "abc", "", "456", "def", "   ", "789", "ghi"]
        assert profile_values(mixed_with_empty, use_incremental_typecheck=True) == DataType.MIXED
        assert profile_values(mixed_with_empty, use_incremental_typecheck=False) == DataType.MIXED

        # Test edge case: only numeric types (should NOT detect MIXED)
        numeric_only = ["123", "1.23", "456", "4.56", "789", "7.89", "012", "0.12"]
        assert profile_values(numeric_only, use_incremental_typecheck=True) == DataType.FLOAT
        assert profile_values(numeric_only, use_incremental_typecheck=False) == DataType.FLOAT

        # Test edge case: only string types (should NOT detect MIXED)
        string_only = ["abc", "def", "ghi", "jkl", "mno", "pqr", "stu", "vwx"]
        assert profile_values(string_only, use_incremental_typecheck=True) == DataType.STRING
        assert profile_values(string_only, use_incremental_typecheck=False) == DataType.STRING

    @pytest.mark.parametrize(
        "case",
        [
            {
                "name": "EMPTY only (should terminate immediately)",
                "data": [""] * 12,
                "expected": DataType.EMPTY,
                "should_terminate_early": True,
            },
            {
                "name": "NONE only (should terminate immediately)",
                "data": [None] * 12,
                "expected": DataType.NONE,
                "should_terminate_early": True,
            },
            {
                "name": "NONE + EMPTY (should terminate early)",
                "data": [None, "", None, "", None, "", None, "", None, "", None, ""],
                "expected": DataType.NONE,
                "should_terminate_early": True,
            },
            {
                "name": "BOOLEAN + EMPTY (should terminate early)",
                "data": [
                    "true",
                    "",
                    "false",
                    "",
                    "true",
                    "",
                    "false",
                    "",
                    "true",
                    "",
                    "false",
                    "",
                ],
                "expected": DataType.BOOLEAN,
                "should_terminate_early": True,
            },
            {
                "name": "STRING + EMPTY (should terminate early)",
                "data": [
                    "abc",
                    "",
                    "def",
                    "",
                    "ghi",
                    "",
                    "jkl",
                    "",
                    "mno",
                    "",
                    "pqr",
                    "",
                ],
                "expected": DataType.STRING,
                "should_terminate_early": True,
            },
            {
                "name": "Integer + String (should detect MIXED early)",
                "data": [
                    "123",
                    "abc",
                    "456",
                    "def",
                    "789",
                    "ghi",
                    "012",
                    "jkl",
                    "345",
                    "mno",
                    "678",
                    "pqr",
                ],
                "expected": DataType.MIXED,
                "should_terminate_early": True,
            },
            {
                "name": "Float + String (should detect MIXED early)",
                "data": [
                    "1.23",
                    "abc",
                    "4.56",
                    "def",
                    "7.89",
                    "ghi",
                    "0.12",
                    "jkl",
                    "3.45",
                    "mno",
                    "6.78",
                    "pqr",
                ],
                "expected": DataType.MIXED,
                "should_terminate_early": True,
            },
            {
                "name": "Date + String (should detect MIXED early)",
                "data": [
                    "2023-01-01",
                    "abc",
                    "2023-01-02",
                    "def",
                    "2023-01-03",
                    "ghi",
                    "2023-01-04",
                    "jkl",
                    "2023-01-05",
                    "mno",
                    "2023-01-06",
                    "pqr",
                ],
                "expected": DataType.MIXED,
                "should_terminate_early": True,
            },
            {
                "name": "Time + String (should detect MIXED early)",
                "data": [
                    "14:30:00",
                    "abc",
                    "15:45:00",
                    "def",
                    "16:00:00",
                    "ghi",
                    "17:15:00",
                    "jkl",
                    "18:30:00",
                    "mno",
                    "19:45:00",
                    "pqr",
                ],
                "expected": DataType.MIXED,
                "should_terminate_early": True,
            },
            {
                "name": "Datetime + String (should detect MIXED early)",
                "data": [
                    "2023-01-01T14:30:00",
                    "abc",
                    "2023-01-02T15:45:00",
                    "def",
                    "2023-01-03T16:00:00",
                    "ghi",
                    "2023-01-04T17:15:00",
                    "jkl",
                ],
                "expected": DataType.MIXED,
                "should_terminate_early": True,
            },
            {
                "name": "Pure INTEGER (requires full analysis for all-digit logic)",
                "data": [str(i) for i in range(12)],
                "expected": DataType.INTEGER,
                "should_terminate_early": False,
            },
            {
                "name": "Pure FLOAT (requires full analysis)",
                "data": [f"{i}.5" for i in range(12)],
                "expected": DataType.FLOAT,
                "should_terminate_early": False,
            },
            {
                "name": "INTEGER + FLOAT (requires full analysis)",
                "data": [
                    "123",
                    "1.23",
                    "456",
                    "4.56",
                    "789",
                    "7.89",
                    "012",
                    "0.12",
                    "345",
                    "3.45",
                    "678",
                    "6.78",
                ],
                "expected": DataType.FLOAT,
                "should_terminate_early": False,
            },
            {
                "name": "All-digit strings (requires full analysis for prioritization)",
                "data": [
                    "20230101",
                    "143000",
                    "12345",
                    "20230102",
                    "154500",
                    "67890",
                    "20230103",
                    "160000",
                    "11111",
                    "20230104",
                    "171500",
                    "22222",
                ],
                "expected": DataType.INTEGER,
                "should_terminate_early": False,
            },
            {
                "name": "Very small dataset (no check points)",
                "data": ["123", "abc"],
                "expected": DataType.MIXED,
            },
            {
                "name": "Dataset exactly at 25% check point",
                "data": ["123", "abc", "456"],  # 3 items, 25% of 12
                "expected": DataType.MIXED,
            },
            {
                "name": "Dataset exactly at 50% check point",
                "data": [
                    "123",
                    "abc",
                    "456",
                    "def",
                    "789",
                    "ghi",
                ],  # 6 items, 50% of 12
                "expected": DataType.MIXED,
            },
            {
                "name": "Dataset exactly at 75% check point",
                "data": [
                    "123",
                    "abc",
                    "456",
                    "def",
                    "789",
                    "ghi",
                    "012",
                    "jkl",
                    "345",
                ],  # 9 items, 75% of 12
                "expected": DataType.MIXED,
            },
        ],
        ids=[
            "row_0",
            "row_1",
            "row_2",
            "row_3",
            "row_4",
            "row_5",
            "row_6",
            "row_7",
            "row_8",
            "row_9",
            "row_10",
            "row_11",
            "row_12",
            "row_13",
            "row_14",
            "row_15",
            "row_16",
            "row_17",
        ],
    )
    def test_profile_values_comprehensive_early_termination(self, case: dict[str, object]):
        """Comprehensive test of all early termination scenarios."""

        # Test data sizes that will trigger check points
        # 25% check point at 3 items, 50% at 6 items, 75% at 9 items
        test_size = 12
        # Test with incremental checking
        result_optimized = profile_values(case["data"], use_incremental_typecheck=True)

        # Test without incremental checking
        result_original = profile_values(case["data"], use_incremental_typecheck=False)

        # Verify results match
        assert result_optimized == case["expected"]
        assert result_original == case["expected"]
        assert result_optimized == result_original
        # Test with incremental checking
        result_optimized = profile_values(case["data"], use_incremental_typecheck=True)

        # Test without incremental checking
        result_original = profile_values(case["data"], use_incremental_typecheck=False)

        # Verify results match
        assert result_optimized == case["expected"]
        assert result_original == case["expected"]
        assert result_optimized == result_original
        result_optimized = profile_values(case["data"], use_incremental_typecheck=True)
        result_original = profile_values(case["data"], use_incremental_typecheck=False)

        assert result_optimized == case["expected"]
        assert result_original == case["expected"]
        assert result_optimized == result_original

        # Test with generators and other iterables
        def gen_mixed():
            yield "123"
            yield "abc"
            yield "456"
            yield "def"
            yield "789"
            yield "ghi"
            yield "012"
            yield "jkl"
            yield "345"
            yield "mno"
            yield "678"
            yield "pqr"

        result_gen_optimized = profile_values(gen_mixed(), use_incremental_typecheck=True)
        result_gen_original = profile_values(gen_mixed(), use_incremental_typecheck=False)

        assert result_gen_optimized == DataType.MIXED
        assert result_gen_original == DataType.MIXED
        assert result_gen_optimized == result_gen_original

        # Test with tuples
        tuple_data = (
            "123",
            "abc",
            "456",
            "def",
            "789",
            "ghi",
            "012",
            "jkl",
            "345",
            "mno",
            "678",
            "pqr",
        )
        result_tuple_optimized = profile_values(tuple_data, use_incremental_typecheck=True)
        result_tuple_original = profile_values(tuple_data, use_incremental_typecheck=False)

        assert result_tuple_optimized == DataType.MIXED
        assert result_tuple_original == DataType.MIXED
        assert result_tuple_optimized == result_tuple_original


class TestUtilityFunctions:
    """Test cases for utility functions"""

    def test_is_list_like(self):
        """Test list-like detection"""
        # Test list types
        assert is_list_like([])
        assert is_list_like([1, 2, 3])

        # Test non-list types
        assert not is_list_like({})
        assert not is_list_like("abc")
        assert not is_list_like(None)
        assert not is_list_like(123)

    def test_is_dict_like(self):
        """Test dict-like detection"""
        # Test dict types
        assert is_dict_like({})
        assert is_dict_like({"a": 1})

        # Test non-dict types
        assert not is_dict_like([])
        assert not is_dict_like("abc")
        assert not is_dict_like(None)
        assert not is_dict_like(123)

    def test_is_iterable(self):
        """Test iterable detection"""
        # Test iterable types
        assert is_iterable([])
        assert is_iterable({})
        assert is_iterable("abc")
        assert is_iterable((1, 2, 3))

        # Test non-iterable types
        assert not is_iterable(None)
        assert not is_iterable(123)
        assert not is_iterable(True)

    def test_is_iterable_not_string(self):
        """Test non-string iterable detection"""
        # Test non-string iterables
        assert is_iterable_not_string([])
        assert is_iterable_not_string({})
        assert is_iterable_not_string((1, 2, 3))

        # Test strings and non-iterables
        assert not is_iterable_not_string("abc")
        assert not is_iterable_not_string(None)
        assert not is_iterable_not_string(123)

    def test_is_empty(self):
        """Test empty value detection"""
        # Test empty values
        assert is_empty(None)
        assert is_empty("")
        assert is_empty(" ")
        assert is_empty([])
        assert is_empty({})
        assert is_empty(())

        # Test non-empty values
        assert not is_empty("abc")
        assert not is_empty([1, 2, 3])
        assert not is_empty({"a": 1})
        assert not is_empty(0)
        assert not is_empty(False)
