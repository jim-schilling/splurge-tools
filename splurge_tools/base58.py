"""
This module provides a class for base-58 encoding and decoding operations.

Copyright (c) 2025 Jim Schilling

This module is licensed under the MIT License.
"""


class Base58Error(Exception):
    """Base class for all base-58 errors."""

class Base58TypeError(Base58Error):
    """Raised when a type error occurs."""

class Base58ValidationError(Base58Error):
    """Raised when base-58 validation fails."""


class Base58:
    """
    A class for base-58 encoding and decoding operations.

    Base-58 is a binary-to-text encoding scheme that uses 58 characters
    to represent binary data. It's commonly used in cryptocurrency
    applications and other systems where binary data needs to be
    represented in a human-readable format.

    This implementation uses the Bitcoin alphabet:
    "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    """

    DIGITS = '123456789'
    ALPHA_UPPER = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
    ALPHA_LOWER = 'abcdefghijkmnopqrstuvwxyz'    
    ALPHABET = DIGITS + ALPHA_UPPER + ALPHA_LOWER 
    _BASE = len(ALPHABET)    
    
    @classmethod
    def encode(cls, data: bytes) -> str:
        """
        Encode binary data to base-58 string.

        Args:
            data: Binary data to encode

        Returns:
            Base-58 encoded string

        Raises:
            Base58TypeError: If input is not bytes
            Base58ValidationError: If input data is empty or invalid
        """
        if not isinstance(data, bytes):
            raise Base58TypeError("Input must be bytes")
        
        if not data:
            raise Base58ValidationError("Cannot encode empty data")

        # Convert bytes to integer
        num = int.from_bytes(data, byteorder="big")

        # Handle zero case
        if num == 0:
            return cls.ALPHABET[0] * len(data)

        # Convert to base-58
        result = ""
        while num > 0:
            num, remainder = divmod(num, cls._BASE)
            result = cls.ALPHABET[remainder] + result

        # Add leading zeros for each leading zero byte in original data
        for byte in data:
            if byte == 0:
                result = cls.ALPHABET[0] + result
            else:
                break

        return result

    @classmethod
    def decode(cls, base58_data: str) -> bytes:
        """
        Decode base-58 string to binary data.

        Args:
            base58_data: Base-58 encoded string

        Returns:
            Decoded binary data

        Raises:
            Base58TypeError: If input is not a string
            Base58ValidationError: If input string is empty or contains invalid characters
        """
        if not isinstance(base58_data, str):
            raise Base58TypeError("Input must be a string")

        if not base58_data:
            raise Base58ValidationError("Cannot decode empty string")

        if not cls.is_valid(base58_data):
            raise Base58ValidationError("Invalid base-58 string")

        # Count leading '1' characters
        leading_ones = 0
        for char in base58_data:
            if char == cls.ALPHABET[0]:
                leading_ones += 1
            else:
                break

        # If all characters are '1', return the appropriate number of zero bytes
        if leading_ones == len(base58_data):
            return b"\x00" * leading_ones

        # Convert base-58 to integer (skip leading ones)
        num = 0
        for char in base58_data[leading_ones:]:
            num = num * cls._BASE + cls.ALPHABET.index(char)

        # Handle case where num is 0 (all remaining chars were '1')
        if num == 0:
            result = b""
        else:
            # Calculate minimum byte length
            byte_length = (num.bit_length() + 7) // 8
            result = num.to_bytes(byte_length, byteorder="big")

        # Add leading zeros for each leading '1' character
        return b"\x00" * leading_ones + result

    @classmethod
    def is_valid(cls, base58_data: str) -> bool:
        """
        Check if a string is valid base-58.

        Args:
            base58_data: String to validate

        Returns:
            True if valid base-58, False otherwise
        """
        if not isinstance(base58_data, str):
            return False

        if not base58_data:
            return False

        try:
            return all(char in cls.ALPHABET for char in base58_data)
        except Exception:
            return False    
