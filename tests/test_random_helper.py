"""
Unit tests for the RandomHelper class.

This module contains comprehensive tests for all methods in the RandomHelper class,
including both secure and non-secure random generation modes.
"""

import unittest
from jpy_tools.random_helper import RandomHelper
from datetime import date, datetime, timedelta


class TestRandomHelper(unittest.TestCase):
    """Test cases for RandomHelper class."""

    def setUp(self):
        """Set up test fixtures."""
        self.helper = RandomHelper()
        self.today = date.today()
        self.now = datetime.now()

    def test_constants(self):
        """Test class constants are correctly defined."""
        self.assertEqual(RandomHelper.INT64_MAX, 2 ** 63 - 1)
        self.assertEqual(RandomHelper.INT64_MIN, -2 ** 63 - 1)
        self.assertEqual(RandomHelper.INT64_MASK, 0x7fff_ffff_ffff_ffff)
        self.assertEqual(len(RandomHelper.ALPHA_CHARS), 52)  # 26 lowercase + 26 uppercase
        self.assertEqual(len(RandomHelper.DIGITS), 10)
        self.assertEqual(len(RandomHelper.ALPHANUMERIC_CHARS), 62)  # 52 letters + 10 digits
        self.assertEqual(len(RandomHelper.BASE58_CHARS), 58)

    def test_as_bytes(self):
        """Test random byte generation."""
        # Test non-secure mode
        bytes1 = RandomHelper.as_bytes(4)
        bytes2 = RandomHelper.as_bytes(4)
        self.assertEqual(len(bytes1), 4)
        self.assertEqual(len(bytes2), 4)
        # Note: bytes1 and bytes2 might be equal by chance, but unlikely

        # Test secure mode
        secure_bytes1 = RandomHelper.as_bytes(4, secure=True)
        secure_bytes2 = RandomHelper.as_bytes(4, secure=True)
        self.assertEqual(len(secure_bytes1), 4)
        self.assertEqual(len(secure_bytes2), 4)

    def test_as_int(self):
        """Test random integer generation."""
        # Test non-secure mode
        int1 = RandomHelper.as_int()
        int2 = RandomHelper.as_int()
        self.assertIsInstance(int1, int)
        self.assertIsInstance(int2, int)
        self.assertTrue(0 <= int1 <= RandomHelper.INT64_MAX)
        self.assertTrue(0 <= int2 <= RandomHelper.INT64_MAX)

        # Test secure mode
        secure_int1 = RandomHelper.as_int(secure=True)
        secure_int2 = RandomHelper.as_int(secure=True)
        self.assertIsInstance(secure_int1, int)
        self.assertIsInstance(secure_int2, int)
        self.assertTrue(0 <= secure_int1 <= RandomHelper.INT64_MAX)
        self.assertTrue(0 <= secure_int2 <= RandomHelper.INT64_MAX)

    def test_as_int_range(self):
        """Test random integer range generation."""
        # Test normal range
        value = RandomHelper.as_int_range(1, 10)
        self.assertTrue(1 <= value <= 10)

        # Test secure mode
        secure_value = RandomHelper.as_int_range(1, 10, secure=True)
        self.assertTrue(1 <= secure_value <= 10)

        # Test edge cases
        with self.assertRaises(ValueError):
            RandomHelper.as_int_range(10, 1)  # lower > upper
        with self.assertRaises(ValueError):
            RandomHelper.as_int_range(RandomHelper.INT64_MIN - 1, 10)  # below min
        with self.assertRaises(ValueError):
            RandomHelper.as_int_range(1, RandomHelper.INT64_MAX + 1)  # above max

    def test_as_float_range(self):
        """Test random float range generation."""
        # Test normal range
        value = RandomHelper.as_float_range(0.0, 1.0)
        self.assertTrue(0.0 <= value <= 1.0)

        # Test negative range
        value = RandomHelper.as_float_range(-1.0, 1.0)
        self.assertTrue(-1.0 <= value <= 1.0)

        # Test edge case
        with self.assertRaises(ValueError):
            RandomHelper.as_float_range(1.0, 0.0)  # lower > upper

    def test_as_string(self):
        """Test random string generation."""
        # Test with custom charset
        value = RandomHelper.as_string(5, "abc")
        self.assertEqual(len(value), 5)
        self.assertTrue(all(c in "abc" for c in value))

        # Test secure mode
        secure_value = RandomHelper.as_string(5, "abc", secure=True)
        self.assertEqual(len(secure_value), 5)
        self.assertTrue(all(c in "abc" for c in secure_value))

        # Test edge cases
        with self.assertRaises(ValueError):
            RandomHelper.as_string(0, "abc")  # length < 1
        with self.assertRaises(ValueError):
            RandomHelper.as_string(5, "")  # empty charset

    def test_as_alpha(self):
        """Test random alphabetic string generation."""
        # Test non-secure mode
        value = RandomHelper.as_alpha(5)
        self.assertEqual(len(value), 5)
        self.assertTrue(all(c in RandomHelper.ALPHA_CHARS for c in value))

        # Test secure mode
        secure_value = RandomHelper.as_alpha(5, secure=True)
        self.assertEqual(len(secure_value), 5)
        self.assertTrue(all(c in RandomHelper.ALPHA_CHARS for c in secure_value))

    def test_as_alphanumeric(self):
        """Test random alphanumeric string generation."""
        # Test non-secure mode
        value = RandomHelper.as_alphanumeric(5)
        self.assertEqual(len(value), 5)
        self.assertTrue(all(c in RandomHelper.ALPHANUMERIC_CHARS for c in value))

        # Test secure mode
        secure_value = RandomHelper.as_alphanumeric(5, secure=True)
        self.assertEqual(len(secure_value), 5)
        self.assertTrue(all(c in RandomHelper.ALPHANUMERIC_CHARS for c in secure_value))

    def test_as_numeric(self):
        """Test random numeric string generation."""
        # Test non-secure mode
        value = RandomHelper.as_numeric(5)
        self.assertEqual(len(value), 5)
        self.assertTrue(all(c in RandomHelper.DIGITS for c in value))

        # Test secure mode
        secure_value = RandomHelper.as_numeric(5, secure=True)
        self.assertEqual(len(secure_value), 5)
        self.assertTrue(all(c in RandomHelper.DIGITS for c in secure_value))

    def test_as_base58(self):
        """Test random Base58 string generation."""
        # Test non-secure mode
        value = RandomHelper.as_base58(5)
        self.assertEqual(len(value), 5)
        self.assertTrue(all(c in RandomHelper.BASE58_CHARS for c in value))

        # Test secure mode
        secure_value = RandomHelper.as_base58(5, secure=True)
        self.assertEqual(len(secure_value), 5)
        self.assertTrue(all(c in RandomHelper.BASE58_CHARS for c in secure_value))

    def test_as_variable_string(self):
        """Test variable length string generation."""
        # Test normal range
        value = RandomHelper.as_variable_string(3, 5, "abc")
        self.assertTrue(3 <= len(value) <= 5)
        self.assertTrue(all(c in "abc" for c in value))

        # Test secure mode
        secure_value = RandomHelper.as_variable_string(3, 5, "abc", secure=True)
        self.assertTrue(3 <= len(secure_value) <= 5)
        self.assertTrue(all(c in "abc" for c in secure_value))

        # Test edge cases
        with self.assertRaises(ValueError):
            RandomHelper.as_variable_string(-1, 5, "abc")  # negative lower bound
        with self.assertRaises(ValueError):
            RandomHelper.as_variable_string(5, 3, "abc")  # lower >= upper

    def test_as_bool(self):
        """Test random boolean generation."""
        # Test non-secure mode
        value = RandomHelper.as_bool()
        self.assertIsInstance(value, bool)

        # Test secure mode
        secure_value = RandomHelper.as_bool(secure=True)
        self.assertIsInstance(secure_value, bool)

    def test_as_masked_string(self):
        """Test masked string generation."""
        # Test with digits and letters
        value = RandomHelper.as_masked_string("###-@@@")
        self.assertEqual(len(value), 7)
        self.assertTrue(all(c in RandomHelper.DIGITS for c in value[:3]))
        self.assertTrue(all(c in RandomHelper.ALPHA_CHARS for c in value[4:]))
        self.assertEqual(value[3], "-")

        # Test secure mode
        secure_value = RandomHelper.as_masked_string("###-@@@", secure=True)
        self.assertEqual(len(secure_value), 7)
        self.assertTrue(all(c in RandomHelper.DIGITS for c in secure_value[:3]))
        self.assertTrue(all(c in RandomHelper.ALPHA_CHARS for c in secure_value[4:]))
        self.assertEqual(secure_value[3], "-")

        # Test edge cases
        with self.assertRaises(ValueError):
            RandomHelper.as_masked_string("")  # empty mask
        with self.assertRaises(ValueError):
            RandomHelper.as_masked_string("---")  # no mask characters

    def test_as_sequenced_string(self):
        """Test sequenced string generation."""
        # Test basic sequence
        values = RandomHelper.as_sequenced_string(3, 3)
        self.assertEqual(len(values), 3)
        self.assertEqual(values, ["000", "001", "002"])

        # Test with prefix and suffix
        values = RandomHelper.as_sequenced_string(3, 3, prefix="ID-", suffix="-END")
        self.assertEqual(len(values), 3)
        self.assertEqual(values, ["ID-000-END", "ID-001-END", "ID-002-END"])

        # Test with start value
        values = RandomHelper.as_sequenced_string(3, 3, start=100)
        self.assertEqual(len(values), 3)
        self.assertEqual(values, ["100", "101", "102"])

        # Test edge cases
        with self.assertRaises(ValueError):
            RandomHelper.as_sequenced_string(0, 3)  # count < 1
        with self.assertRaises(ValueError):
            RandomHelper.as_sequenced_string(3, 0)  # digits < 1
        with self.assertRaises(ValueError):
            RandomHelper.as_sequenced_string(3, 3, start=-1)  # start < 0
        with self.assertRaises(ValueError):
            RandomHelper.as_sequenced_string(1000, 3)  # sequence too long for digits

    def test_as_date(self):
        """Test random date generation."""
        # Test non-secure mode
        value = RandomHelper.as_date(0, 30)
        self.assertIsInstance(value, date)
        self.assertTrue(self.today <= value <= self.today + timedelta(days=30))

        # Test secure mode
        secure_value = RandomHelper.as_date(0, 30, secure=True)
        self.assertIsInstance(secure_value, date)
        self.assertTrue(self.today <= secure_value <= self.today + timedelta(days=30))

        # Test negative days
        value = RandomHelper.as_date(-30, 0)
        self.assertIsInstance(value, date)
        self.assertTrue(self.today - timedelta(days=30) <= value <= self.today)

        # Test edge cases
        with self.assertRaises(ValueError):
            RandomHelper.as_date(10, 5)  # lower > upper
        with self.assertRaises(ValueError):
            RandomHelper.as_date(RandomHelper.INT64_MIN - 1, 10)  # below min
        with self.assertRaises(ValueError):
            RandomHelper.as_date(1, RandomHelper.INT64_MAX + 1)  # above max

    def test_as_datetime(self):
        """Test random datetime generation."""
        # Test non-secure mode
        value = RandomHelper.as_datetime(0, 30)
        self.assertIsInstance(value, datetime)
        self.assertTrue(self.now <= value <= self.now + timedelta(days=30))

        # Test secure mode
        secure_value = RandomHelper.as_datetime(0, 30, secure=True)
        self.assertIsInstance(secure_value, datetime)
        self.assertTrue(self.now <= secure_value <= self.now + timedelta(days=30))

        # Test negative days
        value = RandomHelper.as_datetime(-30, 0)
        self.assertIsInstance(value, datetime)
        self.assertTrue(self.now - timedelta(days=30) <= value <= self.now)

        # Test edge cases
        with self.assertRaises(ValueError):
            RandomHelper.as_datetime(10, 5)  # lower > upper
        with self.assertRaises(ValueError):
            RandomHelper.as_datetime(RandomHelper.INT64_MIN - 1, 10)  # below min
        with self.assertRaises(ValueError):
            RandomHelper.as_datetime(1, RandomHelper.INT64_MAX + 1)  # above max

        # Test datetime components
        value = RandomHelper.as_datetime(0, 1)
        self.assertIsInstance(value.hour, int)
        self.assertIsInstance(value.minute, int)
        self.assertIsInstance(value.second, int)
        self.assertIsInstance(value.microsecond, int)
        self.assertTrue(0 <= value.hour <= 23)
        self.assertTrue(0 <= value.minute <= 59)
        self.assertTrue(0 <= value.second <= 59)
        self.assertTrue(0 <= value.microsecond <= 999999)


if __name__ == '__main__':
    unittest.main() 