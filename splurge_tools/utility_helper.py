"""
Utility functions for Splurge Tools.

This module provides utility functions for base-58 encoding/decoding
and other helper functionality.
"""

from typing import Union

# Private constants
_BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_BASE58_ALPHABET_LENGTH = len(_BASE58_ALPHABET)


class ValidationError(Exception):
    """
    Exception raised for validation errors.
    """
    pass


def encode_base58(data: Union[bytes, bytearray]) -> str:
    """
    Encode binary data to base-58 string.
    
    Args:
        data: Binary data to encode
        
    Returns:
        Base-58 encoded string
        
    Raises:
        ValidationError: If input data is empty or invalid
    """
    if not data:
        raise ValidationError("Input data cannot be empty")
    
    # Convert to bytes if needed
    if isinstance(data, bytearray):
        data = bytes(data)
    
    # Handle all-zero case
    if all(byte == 0 for byte in data):
        return _BASE58_ALPHABET[0] * len(data)
    
    # Convert to integer
    number = int.from_bytes(data, byteorder='big')
    
    # Encode to base-58
    result = ""
    while number > 0:
        number, remainder = divmod(number, _BASE58_ALPHABET_LENGTH)
        result = _BASE58_ALPHABET[remainder] + result
    
    # Add leading zeros for each zero byte in original data
    for byte in data:
        if byte == 0:
            result = _BASE58_ALPHABET[0] + result
        else:
            break
    
    return result


def decode_base58(base58_data: str) -> bytes:
    """
    Decode base-58 string to binary data.
    
    Args:
        base58_data: Base-58 encoded string
        
    Returns:
        Decoded binary data
        
    Raises:
        ValidationError: If input string is empty or contains invalid characters
    """
    if not base58_data:
        raise ValidationError("Input string cannot be empty")
    
    # Validate characters
    for char in base58_data:
        if char not in _BASE58_ALPHABET:
            raise ValidationError(f"Invalid character '{char}' in base-58 string")
    
    # Handle all-'1' case (all zero bytes)
    if all(char == _BASE58_ALPHABET[0] for char in base58_data):
        return b'\x00' * len(base58_data)
    
    # Convert from base-58 to integer
    number = 0
    for char in base58_data:
        number = number * _BASE58_ALPHABET_LENGTH + _BASE58_ALPHABET.index(char)
    
    # Calculate number of bytes needed
    byte_length = (number.bit_length() + 7) // 8
    
    # Convert to bytes
    result = number.to_bytes(byte_length, byteorder='big')
    
    # Add leading zeros for each leading '1' in the encoded string
    leading_zeros = 0
    for char in base58_data:
        if char == _BASE58_ALPHABET[0]:
            leading_zeros += 1
        else:
            break
    
    return b'\x00' * leading_zeros + result


def is_valid_base58(base58_data: str) -> bool:
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
        for char in base58_data:
            if char not in _BASE58_ALPHABET:
                return False
        return True
    except Exception:
        return False
