"""
Tests for Base58 class.

This module contains comprehensive tests for the Base58 class
including encoding/decoding and validation functionality.
"""

import random
import threading
import time

import pytest

from splurge_tools.base58 import Base58, Base58TypeError, Base58ValidationError


# Test cases for Base58 encoding functionality
def test_encode_simple_string():
    """Test encoding a simple string."""
    data = b"Hello World"
    encoded = Base58.encode(data)
    assert isinstance(encoded, str)
    assert len(encoded) > 0

    # Verify round-trip
    decoded = Base58.decode(encoded)
    assert decoded == data


def test_encode_single_byte():
    """Test encoding a single byte."""
    data = b"A"
    encoded = Base58.encode(data)
    assert isinstance(encoded, str)

    decoded = Base58.decode(encoded)
    assert decoded == data


def test_encode_zero_bytes():
    """Test encoding zero bytes."""
    data = b"\x00"
    encoded = Base58.encode(data)
    assert encoded == "1"

    decoded = Base58.decode(encoded)
    assert decoded == data


def test_encode_all_zero_bytes():
    """Test encoding all zero bytes."""
    data = b"\x00\x00\x00"
    encoded = Base58.encode(data)
    assert encoded == "111"

    decoded = Base58.decode(encoded)
    assert decoded == data


def test_encode_mixed_zero_and_data():
    """Test encoding data with leading zeros."""
    data = b"\x00\x00\x01\x02"
    encoded = Base58.encode(data)
    assert isinstance(encoded, str)

    decoded = Base58.decode(encoded)
    assert decoded == data


def test_encode_large_data():
    """Test encoding large data."""
    data = b"x" * 500
    encoded = Base58.encode(data)
    assert isinstance(encoded, str)

    decoded = Base58.decode(encoded)
    assert decoded == data


def test_encode_very_large_data():
    """Test encoding very large data."""
    data = b"x" * 2000
    encoded = Base58.encode(data)
    assert isinstance(encoded, str)

    decoded = Base58.decode(encoded)
    assert decoded == data


def test_encode_unicode_bytes():
    """Test encoding unicode bytes."""
    data = "Hello🚀World".encode()
    encoded = Base58.encode(data)
    assert isinstance(encoded, str)

    decoded = Base58.decode(encoded)
    assert decoded == data


def test_encode_bytearray_input():
    """Test encoding bytearray input raises Base58TypeError."""
    data = bytearray(b"Hello World")
    with pytest.raises(Base58TypeError):
        Base58.encode(data)


def test_encode_boundary_values():
    """Test encoding boundary values."""
    # Test with single byte values
    for i in range(256):
        data = bytes([i])
        encoded = Base58.encode(data)
        decoded = Base58.decode(encoded)
        assert decoded == data


def test_encode_empty_data_raises_error():
    """Test that encoding empty data raises error."""
    with pytest.raises(Base58ValidationError):
        Base58.encode(b"")


# Test cases for Base58 decoding functionality
def test_decode_simple_string():
    """Test decoding a simple string."""
    string = "JxF12TrwUP45BMd"
    decoded = Base58.decode(string)
    assert decoded == b"Hello World"


def test_decode_single_character():
    """Test decoding a single character."""
    decoded = Base58.decode("1")
    assert decoded == b"\x00"


def test_decode_zero_bytes():
    """Test decoding zero bytes."""
    decoded = Base58.decode("111")
    assert decoded == b"\x00\x00\x00"


def test_decode_all_ones():
    """Test decoding all ones (all zero bytes)."""
    length = 10
    string = "1" * length
    decoded = Base58.decode(string)
    assert decoded == b"\x00" * length


def test_decode_very_long_string():
    """Test decoding a very long string."""
    length = 500
    string = "1" * length
    decoded = Base58.decode(string)
    assert decoded == b"\x00" * length


def test_decode_boundary_characters():
    """Test decoding boundary characters."""
    assert Base58.decode("1") == b"\x00"  # First character
    assert Base58.decode("z") == b"9"  # Last character


def test_decode_empty_string_raises_error():
    """Test that decoding empty string raises error."""
    with pytest.raises(Base58ValidationError):
        Base58.decode("")


def test_decode_invalid_characters_raises_error():
    """Test that decoding invalid characters raises error."""
    with pytest.raises(Base58ValidationError):
        Base58.decode("invalid!")


def test_decode_malformed_strings():
    """Test decoding malformed strings."""
    invalid_strings = [
        "0",  # Invalid character
        "O",  # Invalid character
        "I",  # Invalid character
        "l",  # Invalid character
    ]

    for string in invalid_strings:
        with pytest.raises(Base58ValidationError):
            Base58.decode(string)


def test_decode_unicode_strings():
    """Test decoding unicode strings."""
    with pytest.raises(Base58ValidationError):
        Base58.decode("Hello🚀World")


def test_round_trip_encoding():
    """Test round-trip encoding and decoding."""
    test_data = [
        b"Hello World",
        b"",
        b"\x00\x01\x02\x03",
        b"x" * 100,
        b"Unicode: \xf0\x9f\x9a\x80",  # Rocket emoji in UTF-8
    ]

    for data in test_data:
        if data:  # Skip empty data as it raises error
            encoded = Base58.encode(data)
            decoded = Base58.decode(encoded)
            assert decoded == data


# Test cases for Base58 validation functionality
def test_valid_base58_strings():
    """Test validation of valid base-58 strings."""
    valid_strings = [
        "1",
        "z",
        "JxF12TrwUP45BMd",
        "111",
        "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz",
    ]

    for string in valid_strings:
        assert Base58.is_valid(string)


def test_invalid_base58_strings():
    """Test validation of invalid base-58 strings."""
    invalid_strings = [
        "",
        "0",
        "O",
        "I",
        "l",
        "invalid!",
        "Hello World",
        "🚀",
    ]

    for string in invalid_strings:
        assert not Base58.is_valid(string)


def test_edge_cases():
    """Test edge cases for validation."""
    # Test with None
    assert not Base58.is_valid(None)

    # Test with non-string types
    assert not Base58.is_valid(123)
    assert not Base58.is_valid(b"bytes")
    assert not Base58.is_valid(["list"])


def test_validation_with_unicode_strings():
    """Test validation with unicode strings."""
    assert not Base58.is_valid("Hello🚀World")


def test_validation_with_non_string_inputs():
    """Test validation with non-string inputs."""
    non_string_inputs = [
        None,
        123,
        b"bytes",
        ["list"],
        {"dict": "value"},
        (1, 2, 3),
    ]

    for input_val in non_string_inputs:
        assert not Base58.is_valid(input_val)


# Integration tests for Base58 encoding/decoding
def test_cryptographic_key_encoding():
    """Test encoding/decoding cryptographic keys."""
    # Simulate a cryptographic key
    key = b"\x00" * 32  # 32-byte key
    encoded = Base58.encode(key)
    decoded = Base58.decode(encoded)
    assert decoded == key


def test_bitcoin_address_style_encoding():
    """Test encoding/decoding in Bitcoin address style."""
    # Simulate a public key hash (20 bytes)
    public_key_hash = b"\x00" * 20
    encoded = Base58.encode(public_key_hash)
    decoded = Base58.decode(encoded)
    assert decoded == public_key_hash


def test_random_binary_data():
    """Test encoding/decoding random binary data."""
    for _ in range(10):
        # Generate random data of varying lengths
        length = random.randint(1, 100)
        data = bytes(random.randint(0, 255) for _ in range(length))

        encoded = Base58.encode(data)
        decoded = Base58.decode(encoded)
        assert decoded == data


def test_concurrent_encoding_decoding():
    """Test concurrent encoding and decoding operations."""

    def encode_decode_worker():
        data = b"Hello World"
        for _ in range(100):
            encoded = Base58.encode(data)
            decoded = Base58.decode(encoded)
            assert decoded == data

    threads = []
    for _ in range(5):
        thread = threading.Thread(target=encode_decode_worker)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def test_memory_efficiency():
    """Test memory efficiency with large data."""
    # Test with large data to ensure no memory leaks
    data = b"x" * 2000
    for _ in range(50):
        encoded = Base58.encode(data)
        decoded = Base58.decode(encoded)
        assert decoded == data


def test_performance_with_large_data():
    """Test performance with large data."""
    data = b"x" * 1000
    start_time = time.time()

    for _ in range(50):
        encoded = Base58.encode(data)
        decoded = Base58.decode(encoded)
        assert decoded == data

    end_time = time.time()
    duration = end_time - start_time

    # Should complete in reasonable time (less than 5 seconds)
    assert duration < 5.0


# Test cases for error handling and edge cases
def test_encoding_with_none_input():
    """Test encoding with None input."""
    with pytest.raises(Base58TypeError):
        Base58.encode(None)


def test_encoding_with_string_input():
    """Test encoding with string input (should fail)."""
    with pytest.raises(Base58TypeError):
        Base58.encode("Hello World")


def test_decoding_with_none_input():
    """Test decoding with None input."""
    with pytest.raises(Base58TypeError):
        Base58.decode(None)


def test_decoding_with_bytes_input():
    """Test decoding with bytes input (should fail)."""
    with pytest.raises(Base58TypeError):
        Base58.decode(b"Hello World")


def test_base58_type_error_encoding():
    """Test that Base58TypeError is raised for invalid types in encoding."""
    invalid_inputs = [
        "Hello World",  # String instead of bytes
        123,  # Integer
        ["list"],  # List
        {"dict": "value"},  # Dictionary
        (1, 2, 3),  # Tuple
        None,  # None
    ]

    for invalid_input in invalid_inputs:
        with pytest.raises(Base58TypeError):
            Base58.encode(invalid_input)


def test_base58_type_error_decoding():
    """Test that Base58TypeError is raised for invalid types in decoding."""
    invalid_inputs = [
        b"Hello World",  # Bytes instead of string
        123,  # Integer
        ["list"],  # List
        {"dict": "value"},  # Dictionary
        (1, 2, 3),  # Tuple
        None,  # None
    ]

    for invalid_input in invalid_inputs:
        with pytest.raises(Base58TypeError):
            Base58.decode(invalid_input)


def test_validation_with_complex_objects():
    """Test validation with complex objects."""

    class TestObject:
        def __str__(self):
            return "Hello World"

    obj = TestObject()
    assert not Base58.is_valid(obj)


def test_encoding_with_very_small_data():
    """Test encoding with very small data."""
    data = b"\x00"
    encoded = Base58.encode(data)
    decoded = Base58.decode(encoded)
    assert decoded == data


def test_encoding_with_minimum_values():
    """Test encoding with minimum values."""
    min_bytes = b"\x00" * 10
    encoded = Base58.encode(min_bytes)
    decoded = Base58.decode(encoded)
    assert decoded == min_bytes


def test_encoding_with_maximum_values():
    """Test encoding with maximum values."""
    max_bytes = b"\xff" * 10
    encoded = Base58.encode(max_bytes)
    decoded = Base58.decode(encoded)
    assert decoded == max_bytes


# Additional edge case tests
def test_encode_single_byte_edge_cases():
    """Test encoding single bytes with edge case values."""
    edge_cases = [
        (b"\x00", "1"),  # Zero byte
        (b"\x01", "2"),  # First non-zero
        (b"\xff", "5Q"),  # Maximum byte value
        (b"\x7f", "3C"),  # Middle value
    ]

    for data, expected in edge_cases:
        encoded = Base58.encode(data)
        assert encoded == expected
        decoded = Base58.decode(encoded)
        assert decoded == data


def test_encode_trailing_zeros():
    """Test encoding data with trailing zeros (should not add leading zeros)."""
    data = b"\x01\x00\x00"  # Non-zero followed by zeros
    encoded = Base58.encode(data)
    decoded = Base58.decode(encoded)
    assert decoded == data


def test_encode_middle_zeros():
    """Test encoding data with zeros in the middle."""
    data = b"\x01\x00\x02"  # Non-zero, zero, non-zero
    encoded = Base58.encode(data)
    decoded = Base58.decode(encoded)
    assert decoded == data


def test_decode_single_character_edge_cases():
    """Test decoding single characters with edge case values."""
    edge_cases = [
        ("1", b"\x00"),  # First character
        ("2", b"\x01"),  # Second character
        ("z", b"9"),  # Last character
        ("9", b"\x08"),  # Middle character
    ]

    for string, expected in edge_cases:
        decoded = Base58.decode(string)
        assert decoded == expected


def test_decode_mixed_leading_ones():
    """Test decoding strings with mixed leading ones and other characters."""
    # Test with leading ones followed by other characters
    test_cases = [
        ("11", b"\x00\x00"),
        ("12", b"\x00\x01"),
        ("1z", b"\x009"),
        ("1112", b"\x00\x00\x00\x01"),
    ]

    for string, expected in test_cases:
        decoded = Base58.decode(string)
        assert decoded == expected


def test_decode_complex_sequences():
    """Test decoding complex base58 sequences."""
    # Test various combinations of characters
    test_cases = [
        ("123", b"\x00<"),
        ("abc", b"\x01\xb9{"),
        ("xyz", b"\x02\xdf\xa5"),
        ("1a2b3c", b"\x00\x16G\x08\x97"),
    ]

    for string, expected in test_cases:
        decoded = Base58.decode(string)
        assert decoded == expected


def test_encode_decode_round_trip_edge_cases():
    """Test round-trip encoding/decoding with edge cases."""
    edge_cases = [
        b"\x00\x01\x02\x03\x04\x05",  # Sequential bytes
        b"\xff\xfe\xfd\xfc\xfb\xfa",  # Descending bytes
        b"\x00\xff\x00\xff\x00\xff",  # Alternating pattern
        b"\x01\x00\x00\x00\x00\x00",  # Single non-zero with trailing zeros
        b"\x00\x00\x00\x00\x00\x01",  # Leading zeros with single non-zero
        b"\x7f\x80\x81\x82\x83\x84",  # Values around 128
        b"\x00\x7f\xff\x80\x00\xff",  # Mixed pattern
    ]

    for data in edge_cases:
        encoded = Base58.encode(data)
        decoded = Base58.decode(encoded)
        assert decoded == data


def test_validation_edge_cases():
    """Test validation with edge cases."""
    # Test with single characters
    for char in Base58.ALPHABET:
        assert Base58.is_valid(char)

    # Test with empty string
    assert not Base58.is_valid("")

    # Test with whitespace (should be invalid)
    assert not Base58.is_valid(" ")
    assert not Base58.is_valid("  ")
    assert not Base58.is_valid("\t")
    assert not Base58.is_valid("\n")

    # Test with mixed valid/invalid characters
    assert not Base58.is_valid("1a2b3c0")  # Contains '0' which is invalid
    assert not Base58.is_valid("1a2b3cO")  # Contains 'O' which is invalid
    assert not Base58.is_valid("1a2b3cI")  # Contains 'I' which is invalid
    assert not Base58.is_valid("1a2b3cl")  # Contains 'l' which is invalid


def test_decode_very_small_strings():
    """Test decoding very small strings."""
    # Test single character decoding using round-trip verification
    for i, _char in enumerate(Base58.ALPHABET):
        # Instead of assuming direct mapping, check round-trip
        encoded = Base58.encode(bytes([i]))
        assert Base58.decode(encoded) == bytes([i])


def test_encode_decode_boundary_values():
    """Test encoding/decoding at boundary values."""
    # Test with 1 byte values
    for i in range(256):
        data = bytes([i])
        encoded = Base58.encode(data)
        decoded = Base58.decode(encoded)
        assert decoded == data

    # Test with 2 byte values at boundaries
    boundary_2byte = [
        b"\x00\x00",  # Minimum 2-byte value
        b"\x00\x01",  # Small 2-byte value
        b"\x01\x00",  # Medium 2-byte value
        b"\xff\xff",  # Maximum 2-byte value
    ]

    for data in boundary_2byte:
        encoded = Base58.encode(data)
        decoded = Base58.decode(encoded)
        assert decoded == data


def test_decode_invalid_character_positions():
    """Test decoding with invalid characters in different positions."""
    invalid_chars = ["0", "O", "I", "l"]

    for invalid_char in invalid_chars:
        # Test at beginning
        with pytest.raises(Base58ValidationError):
            Base58.decode(invalid_char + "123")

        # Test in middle
        with pytest.raises(Base58ValidationError):
            Base58.decode("12" + invalid_char + "34")

        # Test at end
        with pytest.raises(Base58ValidationError):
            Base58.decode("123" + invalid_char)


def test_encode_decode_unicode_handling():
    """Test handling of unicode strings in validation."""
    # Test with unicode characters that are not in base58 alphabet
    unicode_strings = [
        "Hello🚀World",
        "Test\u00a0String",  # Non-breaking space
        "Test\u200bString",  # Zero-width space
        "Test\u00adString",  # Soft hyphen
        "Test\u2060String",  # Word joiner
    ]

    for string in unicode_strings:
        assert not Base58.is_valid(string)
        with pytest.raises(Base58ValidationError):
            Base58.decode(string)


def test_encode_decode_special_characters():
    """Test handling of special characters."""
    special_chars = [
        "!@#$%^&*()",  # Punctuation
        "[]{}|\\:;\"'",  # Brackets and quotes
        "<>,.?/~`",  # More punctuation
        " \t\n\r",  # Whitespace
    ]

    for string in special_chars:
        assert not Base58.is_valid(string)
        with pytest.raises(Base58ValidationError):
            Base58.decode(string)


def test_decode_very_long_valid_string():
    """Test decoding a very long valid base58 string."""
    # Create a long string of '1's (representing many zero bytes)
    long_string = "1" * 1000
    decoded = Base58.decode(long_string)
    assert decoded == b"\x00" * 1000

    # Test round-trip with this long string
    encoded = Base58.encode(decoded)
    assert encoded == long_string


def test_encode_decode_memory_efficiency_edge_cases():
    """Test memory efficiency with edge case data patterns."""
    # Test with data that has many leading zeros
    data_with_leading_zeros = b"\x00" * 100 + b"\x01"
    encoded = Base58.encode(data_with_leading_zeros)
    decoded = Base58.decode(encoded)
    assert decoded == data_with_leading_zeros

    # Test with data that has many trailing zeros
    data_with_trailing_zeros = b"\x01" + b"\x00" * 100
    encoded = Base58.encode(data_with_trailing_zeros)
    decoded = Base58.decode(encoded)
    assert decoded == data_with_trailing_zeros


def test_decode_overflow_protection():
    """Test that decoding doesn't cause integer overflow."""
    # Test with very long strings that could potentially cause overflow
    # This tests the robustness of the integer arithmetic

    # Create a string that represents a large number
    large_string = "z" * 100  # All 'z' characters represent large values
    decoded = Base58.decode(large_string)
    assert isinstance(decoded, bytes)
    assert len(decoded) > 0

    # Test round-trip
    encoded = Base58.encode(decoded)
    decoded_again = Base58.decode(encoded)
    assert decoded_again == decoded


def test_encode_decode_consistency():
    """Test consistency of encoding/decoding operations."""
    # Test that multiple encodes of the same data produce the same result
    data = b"Hello World"
    encoded1 = Base58.encode(data)
    encoded2 = Base58.encode(data)
    assert encoded1 == encoded2

    # Test that multiple decodes of the same string produce the same result
    decoded1 = Base58.decode(encoded1)
    decoded2 = Base58.decode(encoded2)
    assert decoded1 == decoded2
    assert decoded1 == data


def test_validation_comprehensive():
    """Test comprehensive validation scenarios."""
    # Test all valid characters individually
    for char in Base58.ALPHABET:
        assert Base58.is_valid(char)

    # Test all valid characters together
    assert Base58.is_valid(Base58.ALPHABET)

    # Test invalid characters that look similar to valid ones
    similar_invalid = ["0", "O", "I", "l"]
    for char in similar_invalid:
        assert not Base58.is_valid(char)
        assert not Base58.is_valid("1" + char + "2")

    # Test with numbers that are not in base58
    for i in range(10):
        if str(i) not in Base58.ALPHABET:
            assert not Base58.is_valid(str(i))

    # Test with uppercase letters that are not in base58
    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if char not in Base58.ALPHABET:
            assert not Base58.is_valid(char)

    # Test with lowercase letters that are not in base58
    for char in "abcdefghijklmnopqrstuvwxyz":
        if char not in Base58.ALPHABET:
            assert not Base58.is_valid(char)


def test_validation_edge_case_coverage():
    """Test validation edge cases to improve coverage."""
    # Test with very long strings to ensure the all() function works correctly
    long_valid_string = Base58.ALPHABET * 10  # Repeat the alphabet 10 times
    assert Base58.is_valid(long_valid_string)

    # Test with strings that have many invalid characters
    long_invalid_string = "0" * 1000  # Many invalid characters
    assert not Base58.is_valid(long_invalid_string)

    # Test with mixed valid/invalid characters
    mixed_string = "1a2b3c0OIl" * 100  # Mix of valid and invalid
    assert not Base58.is_valid(mixed_string)


def test_validation_exception_path(monkeypatch):
    """Test the exception path in the try-except block for 100% coverage."""

    class BadAlphabet:
        def __contains__(self, item):
            raise RuntimeError("Test exception")

    # Use monkeypatching to safely test the exception path
    monkeypatch.setattr(Base58, "ALPHABET", BadAlphabet())

    # This should trigger the exception and return False
    result = Base58.is_valid("test")
    assert result is False, f"Expected False, got {result}"

    # Test with a longer string to ensure the exception is triggered
    result2 = Base58.is_valid("longer_test_string")
    assert result2 is False, f"Expected False, got {result2}"

    # Test with empty string to ensure exception path is covered
    result3 = Base58.is_valid("")
    assert result3 is False, f"Expected False, got {result3}"


def test_decode_num_zero_edge_case():
    """Test the edge case where num == 0 after processing non-leading-ones characters."""
    # This tests the specific case where we have leading ones followed by characters
    # that decode to zero, triggering the "if num == 0:" condition

    # Test with "11" - two leading ones, no other characters
    # This should trigger the first return statement
    result1 = Base58.decode("11")
    assert result1 == b"\x00\x00"

    # Test with "111" - three leading ones, no other characters
    result2 = Base58.decode("111")
    assert result2 == b"\x00\x00\x00"

    # Test with "1111" - four leading ones, no other characters
    result3 = Base58.decode("1111")
    assert result3 == b"\x00\x00\x00\x00"
