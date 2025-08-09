"""
Unit tests for the RandomHelper class.

This module contains comprehensive tests for all methods in the RandomHelper class,
including both secure and non-secure random generation modes.
"""

import unittest
from datetime import date, datetime, timedelta

from splurge_tools.random_helper import RandomHelper
from splurge_tools.exceptions import SplurgeRangeError, SplurgeFormatError, SplurgeParameterError


class TestRandomHelper(unittest.TestCase):
    """Test cases for RandomHelper class."""

    def setUp(self):
        """Set up test fixtures."""
        self.helper = RandomHelper()
        self.today = date.today()
        self.now = datetime.now()

    def test_constants(self):
        """Test class constants are correctly defined."""
        self.assertEqual(RandomHelper.INT64_MAX, 2**63 - 1)
        self.assertEqual(RandomHelper.INT64_MIN, -(2**63))
        self.assertEqual(RandomHelper.INT64_MASK, 0x7FFF_FFFF_FFFF_FFFF)
        self.assertEqual(
            len(RandomHelper.ALPHA_CHARS), 52
        )  # 26 lowercase + 26 uppercase
        self.assertEqual(len(RandomHelper.DIGITS), 10)
        self.assertEqual(
            len(RandomHelper.ALPHANUMERIC_CHARS), 62
        )  # 52 letters + 10 digits
        
        # Test new BASE58 constants
        self.assertEqual(len(RandomHelper.BASE58_ALPHA), 49)  # Excludes O, I, l from alphabet (52-3=49)
        self.assertEqual(len(RandomHelper.BASE58_DIGITS), 9)  # Excludes 0 from digits (1-9 = 9)
        self.assertEqual(len(RandomHelper.BASE58_CHARS), 58)  # 49 + 9 = 58
        self.assertEqual(RandomHelper.BASE58_CHARS, RandomHelper.BASE58_ALPHA + RandomHelper.BASE58_DIGITS)
        
        # Test SYMBOLS constant
        expected_symbols = "!@#$%^&*()_+-=[]{};:,.<>?`~"
        self.assertEqual(RandomHelper.SYMBOLS, expected_symbols)
        self.assertEqual(len(RandomHelper.SYMBOLS), len(expected_symbols))
        
        # Verify BASE58 excludes problematic characters
        excluded_chars = "0OIl"
        for char in excluded_chars:
            self.assertNotIn(char, RandomHelper.BASE58_CHARS, 
                           f"BASE58_CHARS should not contain '{char}'")
        
        # Verify BASE58_DIGITS only contains 1-9
        self.assertEqual(RandomHelper.BASE58_DIGITS, "123456789")
        # Verify BASE58_ALPHA excludes O, I, l
        excluded_alpha = set("OIl")
        self.assertTrue(excluded_alpha.isdisjoint(set(RandomHelper.BASE58_ALPHA)),
                       "BASE58_ALPHA should not contain O, I, or l")

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
        with self.assertRaises(SplurgeRangeError):
            RandomHelper.as_int_range(10, 1)  # lower > upper
        with self.assertRaises(SplurgeRangeError):
            RandomHelper.as_int_range(RandomHelper.INT64_MIN - 1, 10)  # below min
        with self.assertRaises(SplurgeRangeError):
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
        with self.assertRaises(SplurgeRangeError):
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
        with self.assertRaises(SplurgeRangeError):
            RandomHelper.as_string(0, "abc")  # length < 1
        with self.assertRaises(SplurgeParameterError):
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

    def test_as_base58_like(self):
        """Test Base58-like string generation with guaranteed character diversity."""
        import re
        
        # Test 1: Default usage with all symbol types
        result = RandomHelper.as_base58_like(10)
        self.assertEqual(len(result), 10)
        self.assertTrue(re.search(r'[A-HJ-NP-Za-kmnp-z]', result), "Should contain BASE58_ALPHA")
        self.assertTrue(re.search(r'[1-9]', result), "Should contain BASE58_DIGITS")
        self.assertTrue(any(c in RandomHelper.SYMBOLS for c in result), "Should contain symbols")
        
        # Test 2: Without symbols
        result_no_symbols = RandomHelper.as_base58_like(5, symbols="")
        self.assertEqual(len(result_no_symbols), 5)
        self.assertTrue(re.search(r'[A-HJ-NP-Za-kmnp-z]', result_no_symbols), "Should contain BASE58_ALPHA")
        self.assertTrue(re.search(r'[1-9]', result_no_symbols), "Should contain BASE58_DIGITS")
        self.assertFalse(any(c in RandomHelper.SYMBOLS for c in result_no_symbols), "Should not contain symbols")
        
        # Test 3: Custom symbols subset
        custom_symbols = "!@#$"
        result_custom = RandomHelper.as_base58_like(8, symbols=custom_symbols)
        self.assertEqual(len(result_custom), 8)
        self.assertTrue(re.search(r'[A-HJ-NP-Za-kmnp-z]', result_custom), "Should contain BASE58_ALPHA")
        self.assertTrue(re.search(r'[1-9]', result_custom), "Should contain BASE58_DIGITS")
        self.assertTrue(any(c in custom_symbols for c in result_custom), "Should contain custom symbols")
        
        # Test 4: Secure mode
        result_secure = RandomHelper.as_base58_like(6, secure=True)
        self.assertEqual(len(result_secure), 6)
        self.assertTrue(re.search(r'[A-HJ-NP-Za-kmnp-z]', result_secure), "Should contain BASE58_ALPHA")
        self.assertTrue(re.search(r'[1-9]', result_secure), "Should contain BASE58_DIGITS")
        
        # Test 5: Minimum sizes
        min_no_symbols = RandomHelper.as_base58_like(2, symbols="")
        self.assertEqual(len(min_no_symbols), 2)
        
        min_with_symbols = RandomHelper.as_base58_like(3, symbols="!")
        self.assertEqual(len(min_with_symbols), 3)
        self.assertTrue("!" in min_with_symbols, "Should contain the required symbol")
        
        # Test 6: Single symbol
        single_symbol_result = RandomHelper.as_base58_like(4, symbols="@")
        self.assertEqual(len(single_symbol_result), 4)
        self.assertTrue("@" in single_symbol_result, "Should contain the single symbol")
        
        # Test 7: Character diversity verification (run multiple times)
        for _ in range(10):
            diverse_result = RandomHelper.as_base58_like(6, symbols="!@")
            has_alpha = bool(re.search(r'[A-HJ-NP-Za-kmnp-z]', diverse_result))
            has_digit = bool(re.search(r'[1-9]', diverse_result))
            has_symbol = bool(re.search(r'[!@]', diverse_result))
            self.assertTrue(has_alpha, f"Result '{diverse_result}' should have alpha character")
            self.assertTrue(has_digit, f"Result '{diverse_result}' should have digit character")
            self.assertTrue(has_symbol, f"Result '{diverse_result}' should have symbol character")

    def test_as_base58_like_error_conditions(self):
        """Test error conditions for as_base58_like method."""
        
        # Test 1: Invalid size
        with self.assertRaises(SplurgeRangeError) as cm:
            RandomHelper.as_base58_like(0)
        self.assertIn("size must be >= 1", str(cm.exception))
        
        # Test 2: Size too small for requirements (with symbols)
        with self.assertRaises(SplurgeRangeError) as cm:
            RandomHelper.as_base58_like(2, symbols="!")
        self.assertIn("Size too small to guarantee character diversity", str(cm.exception))
        
        # Test 3: Size too small for requirements (without symbols)
        with self.assertRaises(SplurgeRangeError) as cm:
            RandomHelper.as_base58_like(1, symbols="")
        self.assertIn("Size too small to guarantee character diversity", str(cm.exception))
        
        # Test 4: Invalid symbols (not in SYMBOLS constant)
        with self.assertRaises(SplurgeFormatError) as cm:
            RandomHelper.as_base58_like(5, symbols="XYZ")
        self.assertIn("Invalid characters in symbols parameter", str(cm.exception))
        
        # Test 5: Mixed valid and invalid symbols
        with self.assertRaises(SplurgeFormatError) as cm:
            RandomHelper.as_base58_like(5, symbols="!@XY")
        self.assertIn("Invalid characters in symbols parameter", str(cm.exception))
        
        # Test 6: Symbols with characters from BASE58 set (should fail)
        with self.assertRaises(SplurgeFormatError) as cm:
            RandomHelper.as_base58_like(5, symbols="A1!")  # A and 1 are from BASE58, not SYMBOLS
        self.assertIn("Invalid characters in symbols parameter", str(cm.exception))

    def test_as_base58_like_constants_validation(self):
        """Test that the method correctly uses the updated constants."""
        # Verify BASE58_ALPHA and BASE58_DIGITS are used correctly
        result = RandomHelper.as_base58_like(10, symbols="")
        
        # Should only contain BASE58_ALPHA and BASE58_DIGITS
        allowed_chars = RandomHelper.BASE58_ALPHA + RandomHelper.BASE58_DIGITS
        self.assertTrue(all(c in allowed_chars for c in result), 
                       f"Result '{result}' contains characters not in BASE58_ALPHA + BASE58_DIGITS")
        
        # Should not contain excluded characters (0, O, I, l from original base58)
        excluded_chars = "0OIl"
        self.assertFalse(any(c in excluded_chars for c in result),
                        f"Result '{result}' should not contain excluded characters: {excluded_chars}")

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
        with self.assertRaises(SplurgeRangeError):
            RandomHelper.as_variable_string(-1, 5, "abc")  # negative lower bound
        with self.assertRaises(SplurgeRangeError):
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
        with self.assertRaises(SplurgeFormatError):
            RandomHelper.as_masked_string("")  # empty mask
        with self.assertRaises(SplurgeFormatError):
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
        with self.assertRaises(SplurgeRangeError):
            RandomHelper.as_sequenced_string(0, 3)  # count < 1
        with self.assertRaises(SplurgeRangeError):
            RandomHelper.as_sequenced_string(3, 0)  # digits < 1
        with self.assertRaises(SplurgeRangeError):
            RandomHelper.as_sequenced_string(3, 3, start=-1)  # start < 0
        with self.assertRaises(SplurgeRangeError):
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

        # Test with base_date
        base_date = date(2024, 1, 1)
        value = RandomHelper.as_date(0, 30, base_date=base_date)
        self.assertIsInstance(value, date)
        self.assertTrue(base_date <= value <= base_date + timedelta(days=30))

        # Test negative days
        value = RandomHelper.as_date(-30, 0)
        self.assertIsInstance(value, date)
        self.assertTrue(self.today - timedelta(days=30) <= value <= self.today)

        # Test edge cases
        with self.assertRaises(SplurgeRangeError):
            RandomHelper.as_date(10, 5)  # lower > upper
        with self.assertRaises(SplurgeRangeError):
            RandomHelper.as_date(RandomHelper.INT64_MIN - 1, 10)  # below min
        with self.assertRaises(SplurgeRangeError):
            RandomHelper.as_date(1, RandomHelper.INT64_MAX + 1)  # above max

    def test_as_datetime(self):
        """Test random datetime generation."""
        # Test non-secure mode
        value = RandomHelper.as_datetime(0, 30)
        self.assertIsInstance(value, datetime)
        # Compare only date components
        self.assertTrue(value.date() >= self.now.date())
        self.assertTrue(value.date() <= (self.now + timedelta(days=30)).date())

        # Test secure mode
        secure_value = RandomHelper.as_datetime(0, 30, secure=True)
        self.assertIsInstance(secure_value, datetime)
        # Compare only date components
        self.assertTrue(secure_value.date() >= self.now.date())
        self.assertTrue(secure_value.date() <= (self.now + timedelta(days=30)).date())

        # Test with base_date
        base_date = datetime(2024, 1, 1, 12, 0, 0)
        value = RandomHelper.as_datetime(0, 30, base_date=base_date)
        self.assertIsInstance(value, datetime)
        # Compare only date components
        self.assertTrue(value.date() >= base_date.date())
        self.assertTrue(value.date() <= (base_date + timedelta(days=30)).date())
        # Verify time components are randomized
        self.assertIsInstance(value.hour, int)
        self.assertIsInstance(value.minute, int)
        self.assertIsInstance(value.second, int)
        self.assertIsInstance(value.microsecond, int)
        self.assertTrue(0 <= value.hour <= 23)
        self.assertTrue(0 <= value.minute <= 59)
        self.assertTrue(0 <= value.second <= 59)
        self.assertTrue(0 <= value.microsecond <= 999999)

        # Test negative days
        value = RandomHelper.as_datetime(-30, 0)
        self.assertIsInstance(value, datetime)
        # Compare only date components
        self.assertTrue(value.date() >= (self.now - timedelta(days=30)).date())
        self.assertTrue(value.date() <= self.now.date())

        # Test edge cases
        with self.assertRaises(SplurgeRangeError):
            RandomHelper.as_datetime(10, 5)  # lower > upper
        with self.assertRaises(SplurgeRangeError):
            RandomHelper.as_datetime(RandomHelper.INT64_MIN - 1, 10)  # below min
        with self.assertRaises(SplurgeRangeError):
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


if __name__ == "__main__":
    unittest.main()
