"""
Unit tests for type_helper module
"""
import unittest
from datetime import datetime, date
from jpy_tools.type_helper import (
    String, DataType, profile_values, is_list_like, is_dict_like,
    is_iterable, is_iterable_not_string, is_empty
)


class TestString(unittest.TestCase):
    """Test cases for String class methods"""

    def test_is_bool_like(self):
        """Test boolean-like value detection"""
        # Test boolean values
        self.assertTrue(String.is_bool_like(True))
        self.assertTrue(String.is_bool_like(False))
        
        # Test string values
        self.assertTrue(String.is_bool_like('true'))
        self.assertTrue(String.is_bool_like('false'))
        self.assertTrue(String.is_bool_like('TRUE'))
        self.assertTrue(String.is_bool_like('FALSE'))
        
        # Test with whitespace
        self.assertTrue(String.is_bool_like(' true '))
        self.assertTrue(String.is_bool_like(' false '))
        
        # Test non-boolean values
        self.assertFalse(String.is_bool_like('yes'))
        self.assertFalse(String.is_bool_like('no'))
        self.assertFalse(String.is_bool_like(None))
        self.assertFalse(String.is_bool_like(1))
        self.assertFalse(String.is_bool_like(0))

    def test_is_none_like(self):
        """Test None-like value detection"""
        # Test None values
        self.assertTrue(String.is_none_like(None))
        
        # Test string values
        self.assertTrue(String.is_none_like('none'))
        self.assertTrue(String.is_none_like('null'))
        self.assertTrue(String.is_none_like('NONE'))
        self.assertTrue(String.is_none_like('NULL'))
        
        # Test with whitespace
        self.assertTrue(String.is_none_like(' none '))
        self.assertTrue(String.is_none_like(' null '))
        
        # Test non-None values
        self.assertFalse(String.is_none_like(''))
        self.assertFalse(String.is_none_like('0'))
        self.assertFalse(String.is_none_like(0))
        self.assertFalse(String.is_none_like([]))

    def test_is_float_like(self):
        """Test float-like value detection"""
        # Test float values
        self.assertTrue(String.is_float_like(1.23))
        self.assertTrue(String.is_float_like(-1.23))
        
        # Test string values
        self.assertTrue(String.is_float_like('1.23'))
        self.assertTrue(String.is_float_like('-1.23'))
        self.assertTrue(String.is_float_like('.23'))
        self.assertTrue(String.is_float_like('1.'))
        
        # Test with whitespace
        self.assertTrue(String.is_float_like(' 1.23 '))
        
        # Test non-float values
        self.assertFalse(String.is_float_like('1,23'))
        self.assertFalse(String.is_float_like('abc'))
        self.assertFalse(String.is_float_like(None))
        self.assertFalse(String.is_float_like([]))

    def test_is_int_like(self):
        """Test integer-like value detection"""
        # Test integer values
        self.assertTrue(String.is_int_like(123))
        self.assertTrue(String.is_int_like(-123))
        
        # Test string values
        self.assertTrue(String.is_int_like('123'))
        self.assertTrue(String.is_int_like('-123'))
        
        # Test with whitespace
        self.assertTrue(String.is_int_like(' 123 '))
        
        # Test non-integer values
        self.assertFalse(String.is_int_like('123.45'))
        self.assertFalse(String.is_int_like('abc'))
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
        self.assertTrue(String.is_numeric_like('123'))
        self.assertTrue(String.is_numeric_like('123.45'))
        self.assertTrue(String.is_numeric_like('-123'))
        self.assertTrue(String.is_numeric_like('-123.45'))
        
        # Test non-numeric values
        self.assertFalse(String.is_numeric_like('abc'))
        self.assertFalse(String.is_numeric_like(None))
        self.assertFalse(String.is_numeric_like([]))

    def test_is_date_like(self):
        """Test date-like value detection"""
        # Test date values
        test_date = date(2023, 1, 1)
        self.assertTrue(String.is_date_like(test_date))
        
        # Test string values
        self.assertTrue(String.is_date_like('2023-01-01'))
        self.assertTrue(String.is_date_like('2023/01/01'))
        self.assertTrue(String.is_date_like('01-01-2023'))
        self.assertTrue(String.is_date_like('01/01/2023'))
        
        # Test with whitespace
        self.assertTrue(String.is_date_like(' 2023-01-01 '))
        
        # Test non-date values
        self.assertFalse(String.is_date_like('2023-13-27'))  # Invalid month
        self.assertFalse(String.is_date_like('abc'))
        self.assertFalse(String.is_date_like(None))
        self.assertFalse(String.is_date_like([]))

    def test_is_datetime_like(self):
        """Test datetime-like value detection"""
        # Test datetime values
        test_datetime = datetime(2023, 1, 1, 12, 30, 45)
        self.assertTrue(String.is_datetime_like(test_datetime))
        
        # Test string values
        self.assertTrue(String.is_datetime_like('2023-01-01T12:30:45'))
        self.assertTrue(String.is_datetime_like('2023-01-01T12:30:45.12340'))
        self.assertTrue(String.is_datetime_like('2023/01/01T12:30:45'))
        
        # Test with whitespace
        self.assertTrue(String.is_datetime_like(' 2023-01-01T12:30:45 '))
        
        # Test non-datetime values
        self.assertFalse(String.is_datetime_like('2023-13-27T12:30:45'))  # Invalid month
        self.assertFalse(String.is_datetime_like('abc'))
        self.assertFalse(String.is_datetime_like(None))
        self.assertFalse(String.is_datetime_like([]))

    def test_to_bool(self):
        """Test boolean conversion"""
        # Test boolean values
        self.assertTrue(String.to_bool(True))
        self.assertFalse(String.to_bool(False))
        
        # Test string values
        self.assertTrue(String.to_bool('true'))
        self.assertFalse(String.to_bool('false'))
        
        # Test with default
        self.assertIsNone(String.to_bool('invalid', default=None))
        self.assertFalse(String.to_bool('invalid', default=False))
        
        # Test with whitespace
        self.assertTrue(String.to_bool(' true '))
        self.assertFalse(String.to_bool(' false '))

    def test_to_float(self):
        """Test float conversion"""
        # Test float values
        self.assertEqual(String.to_float(1.23), 1.23)
        self.assertEqual(String.to_float(-1.23), -1.23)
        
        # Test string values
        self.assertEqual(String.to_float('1.23'), 1.23)
        self.assertEqual(String.to_float('-1.23'), -1.23)
        
        # Test with default
        self.assertIsNone(String.to_float('invalid', default=None))
        self.assertEqual(String.to_float('invalid', default=0.0), 0.0)
        
        # Test with whitespace
        self.assertEqual(String.to_float(' 1.23 '), 1.23)

    def test_to_int(self):
        """Test integer conversion"""
        # Test integer values
        self.assertEqual(String.to_int(123), 123)
        self.assertEqual(String.to_int(-123), -123)
        
        # Test string values
        self.assertEqual(String.to_int('123'), 123)
        self.assertEqual(String.to_int('-123'), -123)
        
        # Test with default
        self.assertIsNone(String.to_int('invalid', default=None))
        self.assertEqual(String.to_int('invalid', default=0), 0)
        
        # Test with whitespace
        self.assertEqual(String.to_int(' 123 '), 123)

    def test_to_date(self):
        """Test date conversion"""
        # Test date values
        test_date = date(2023, 1, 1)
        self.assertEqual(String.to_date(test_date), test_date)
        
        # Test string values
        self.assertEqual(String.to_date('2023-01-01'), date(2023, 1, 1))
        self.assertEqual(String.to_date('2023/01/01'), date(2023, 1, 1))
        
        # Test with default
        self.assertIsNone(String.to_date('invalid', default=None))
        default_date = date(2023, 1, 1)
        self.assertEqual(String.to_date('invalid', default=default_date), default_date)
        
        # Test with whitespace
        self.assertEqual(String.to_date(' 2023-01-01 '), date(2023, 1, 1))

    def test_to_datetime(self):
        """Test datetime conversion"""
        # Test datetime values
        test_datetime = datetime(2023, 1, 1, 12, 30, 45)
        self.assertEqual(String.to_datetime(test_datetime), test_datetime)
        
        # Test string values
        self.assertEqual(
            String.to_datetime('2023-01-01T12:30:45'),
            datetime(2023, 1, 1, 12, 30, 45)
        )
        
        # Test with default
        self.assertIsNone(String.to_datetime('invalid', default=None))
        default_datetime = datetime(2023, 1, 1, 12, 30, 45)
        self.assertEqual(
            String.to_datetime('invalid', default=default_datetime),
            default_datetime
        )
        
        # Test with whitespace
        self.assertEqual(
            String.to_datetime(' 2023-01-01T12:30:45 '),
            datetime(2023, 1, 1, 12, 30, 45)
        )

    def test_has_leading_zero(self):
        """Test leading zero detection"""
        # Test with leading zero
        self.assertTrue(String.has_leading_zero('01'))
        self.assertTrue(String.has_leading_zero(' 01 '))
        
        # Test without leading zero
        self.assertFalse(String.has_leading_zero('1'))
        self.assertFalse(String.has_leading_zero('10'))
        self.assertFalse(String.has_leading_zero(None))
        self.assertFalse(String.has_leading_zero(''))

    def test_infer_type(self):
        """Test type inference"""
        # Test basic types
        self.assertEqual(String.infer_type(None), DataType.NONE)
        self.assertEqual(String.infer_type(True), DataType.BOOLEAN)
        self.assertEqual(String.infer_type(123), DataType.INTEGER)
        self.assertEqual(String.infer_type(123.45), DataType.FLOAT)
        self.assertEqual(String.infer_type('abc'), DataType.STRING)
        
        # Test date types
        self.assertEqual(
            String.infer_type(date(2023, 1, 1)),
            DataType.DATE
        )
        self.assertEqual(
            String.infer_type(datetime(2023, 1, 1, 12, 30, 45)),
            DataType.DATETIME
        )
        
        # Test string representations
        self.assertEqual(String.infer_type('2023-01-01'), DataType.DATE)
        self.assertEqual(
            String.infer_type('2023-01-01T12:30:45'),
            DataType.DATETIME
        )
        self.assertEqual(String.infer_type('123'), DataType.INTEGER)
        self.assertEqual(String.infer_type('123.45'), DataType.FLOAT)
        self.assertEqual(String.infer_type('true'), DataType.BOOLEAN)


class TestProfileValues(unittest.TestCase):
    """Test cases for profile_values function"""

    def test_profile_values(self):
        """Test value profiling"""
        # Test homogeneous types
        self.assertEqual(
            profile_values([1, 2, 3]),
            DataType.INTEGER
        )
        self.assertEqual(
            profile_values([1.1, 2.2, 3.3]),
            DataType.FLOAT
        )
        self.assertEqual(
            profile_values(['a', 'b', 'c']),
            DataType.STRING
        )
        self.assertEqual(
            profile_values([True, False]),
            DataType.BOOLEAN
        )
        
        # Test mixed types
        self.assertEqual(
            profile_values([1, 'a', 2.0]),
            DataType.MIXED
        )
        
        # Test empty values
        self.assertEqual(
            profile_values([None, None, None]),
            DataType.NONE
        )
        
        # Test invalid input
        with self.assertRaises(ValueError):
            profile_values('not iterable')


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions"""

    def test_is_list_like(self):
        """Test list-like detection"""
        # Test list types
        self.assertTrue(is_list_like([]))
        self.assertTrue(is_list_like([1, 2, 3]))
        
        # Test non-list types
        self.assertFalse(is_list_like({}))
        self.assertFalse(is_list_like('abc'))
        self.assertFalse(is_list_like(None))
        self.assertFalse(is_list_like(123))

    def test_is_dict_like(self):
        """Test dict-like detection"""
        # Test dict types
        self.assertTrue(is_dict_like({}))
        self.assertTrue(is_dict_like({'a': 1}))
        
        # Test non-dict types
        self.assertFalse(is_dict_like([]))
        self.assertFalse(is_dict_like('abc'))
        self.assertFalse(is_dict_like(None))
        self.assertFalse(is_dict_like(123))

    def test_is_iterable(self):
        """Test iterable detection"""
        # Test iterable types
        self.assertTrue(is_iterable([]))
        self.assertTrue(is_iterable({}))
        self.assertTrue(is_iterable('abc'))
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
        self.assertFalse(is_iterable_not_string('abc'))
        self.assertFalse(is_iterable_not_string(None))
        self.assertFalse(is_iterable_not_string(123))

    def test_is_empty(self):
        """Test empty value detection"""
        # Test empty values
        self.assertTrue(is_empty(None))
        self.assertTrue(is_empty(''))
        self.assertTrue(is_empty(' '))
        self.assertTrue(is_empty([]))
        self.assertTrue(is_empty({}))
        self.assertTrue(is_empty(()))
        
        # Test non-empty values
        self.assertFalse(is_empty('abc'))
        self.assertFalse(is_empty([1, 2, 3]))
        self.assertFalse(is_empty({'a': 1}))
        self.assertFalse(is_empty(0))
        self.assertFalse(is_empty(False))


if __name__ == '__main__':
    unittest.main() 