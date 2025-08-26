"""
Random helper module providing secure and non-secure random number generation utilities.
This module offers functions for generating random integers, strings, booleans, and more,
with options for both cryptographically secure and non-secure random generation.

The module uses Python's built-in `secrets` module for secure generation and `random` module
for non-secure generation. All methods support both secure and non-secure modes via the
`secure` parameter.

Copyright (c) 2025 Jim Schilling.

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import random
import string
import sys
from datetime import date, datetime, timedelta
from secrets import randbits
from typing import List

from splurge_tools.exceptions import SplurgeParameterError, SplurgeRangeError, SplurgeFormatError


class RandomHelper:
    """
    A utility class for generating various types of random values.

    This class provides methods for generating random integers, strings, booleans, and more.
    All methods support both cryptographically secure (using secrets module) and non-secure
    (using random module) generation modes.

    Attributes:
        INT64_MAX (int): Maximum value for 64-bit signed integer (2^63 - 1)
        INT64_MIN (int): Minimum value for 64-bit signed integer (-2^63)
        INT64_MASK (int): Bit mask for 64-bit integers (0x7fff_ffff_ffff_ffff)
        ALPHA_CHARS (str): All ASCII letters (a-z, A-Z)
        DIGITS (str): All decimal digits (0-9)
        ALPHANUMERIC_CHARS (str): Combination of letters and digits
        BASE58_CHARS (str): Base58 character set (excluding 0, O, I, l)
    """

    INT64_MAX: int = 2**63 - 1
    INT64_MIN: int = -(2**63)
    INT64_MASK: int = 0x7FFF_FFFF_FFFF_FFFF
    ALPHA_CHARS: str = f"{string.ascii_lowercase}{string.ascii_uppercase}"
    DIGITS: str = "0123456789"
    ALPHANUMERIC_CHARS: str = f"{ALPHA_CHARS}{DIGITS}"
    BASE58_ALPHA: str = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    BASE58_DIGITS: str = "123456789"
    BASE58_CHARS: str = f"{BASE58_DIGITS}{BASE58_ALPHA}"
    SYMBOLS: str = "!@#$%^&*()_+-=[]{};:,.<>?`~"

    @staticmethod
    def as_bytes(
        size: int,
        *,
        secure: bool | None = False
    ) -> bytes:
        """
        Generate random bytes of specified size.

        Args:
            size (int): Number of bytes to generate
            secure (bool, optional): If True, uses secrets.randbits() for cryptographically
                secure generation. If False, uses random.randbytes(). Defaults to False.

        Returns:
            bytes: Random bytes of specified size

        Example:
            >>> RandomHelper.as_bytes(4)
            b'\x12\x34\x56\x78'
            >>> RandomHelper.as_bytes(4, secure=True)  # Cryptographically secure
            b'\x9a\xb2\xc3\xd4'
        """
        if secure:
            bits: int = randbits(size * 8)
            return bits.to_bytes(size, sys.byteorder)
        return random.randbytes(size)

    @classmethod
    def as_int(
        cls,
        size: int = 8,
        *,
        secure: bool | None = False
    ) -> int:
        """
        Generate a random 64-bit integer.

        Args:
            size (int, optional): Number of bytes to generate. Defaults to 8.
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            int: Random 64-bit integer between 0 and 2^63-1

        Example:
            >>> RandomHelper.as_int()
            1234567890123456789
            >>> RandomHelper.as_int(secure=True)  # Cryptographically secure
            9876543210987654321
        """
        return (
            int.from_bytes(cls.as_bytes(size, secure=secure), sys.byteorder)
            & cls.INT64_MAX
        )

    @classmethod
    def as_int_range(
        cls,
        lower: int,
        upper: int,
        *,
        secure: bool | None = False
    ) -> int:
        """
        Generate a random 64-bit integer within a specified range.

        Args:
            lower (int): Lower bound (inclusive)
            upper (int): Upper bound (inclusive)
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            int: Random 64-bit integer between lower and upper (inclusive)

        Raises:
            ValueError: If lower >= upper or range is outside valid 64-bit bounds

        Example:
            >>> random_int_range(1000000, 2000000)
            1567890
            >>> random_int_range(1000000, 2000000, secure=True)  # Cryptographically secure
            1789012
        """
        if lower >= upper:
            raise SplurgeRangeError(
                "lower must be < upper",
                details=f"Got lower={lower}, upper={upper}"
            )
        
        if lower < cls.INT64_MIN or upper > cls.INT64_MAX:
            raise SplurgeRangeError(
                f"Range {lower} to {upper} exceeds 64-bit integer bounds",
                details=f"Valid range: {cls.INT64_MIN} to {cls.INT64_MAX}"
            )
        return int(cls.as_int(secure=secure) % (upper - lower + 1)) + lower

    @classmethod
    def as_float_range(
        cls,
        lower: float,
        upper: float,
        *,
        secure: bool | None = False
    ) -> float:
        """
        Generate a random float within a specified range.

        Args:
            lower (float): Lower bound (inclusive)
            upper (float): Upper bound (inclusive)
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            float: Random float between lower and upper (inclusive)

        Raises:
            ValueError: If lower >= upper

        Example:
            >>> RandomHelper.as_float_range(0.0, 1.0)
            0.56789
            >>> RandomHelper.as_float_range(-1.0, 1.0, secure=True)  # Cryptographically secure
            0.12345
        """
        if lower >= upper:
            raise SplurgeRangeError(
                "lower must be < upper",
                details=f"Got lower={lower}, upper={upper}"
            )
        
        if secure:
            # Use secure random generation
            range_size = upper - lower
            # Generate secure random bytes and convert to float in range [0, 1)
            random_bytes = cls.as_bytes(8, secure=True)
            random_int = int.from_bytes(random_bytes, 'big')
            # Convert to float in range [0, 1)
            random_fraction = random_int / (2**64)
            return lower + (random_fraction * range_size)
        else:
            return random.uniform(lower, upper)

    @classmethod
    def as_string(
        cls,
        length: int,
        allowable_chars: str,
        *,
        secure: bool | None = False
    ) -> str:
        """
        Generate a random string of specified length using given characters.

        Args:
            length (int): Length of the string to generate
            allowable_chars (str): Characters to use in the random string
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            str: Random string of specified length

        Raises:
            ValueError: If length < 1 or allowable_chars is empty

        Example:
            >>> random_string(5, "abc")
            'abcba'
            >>> random_string(10, RandomHelperConstants.ALPHANUMERIC_CHARS)
            'aB3cD4eF5g'
        """
        if not isinstance(length, int):
            raise SplurgeParameterError(
                f"length must be an integer, got {type(length).__name__}",
                details=f"Expected integer, received: {repr(length)}"
            )
        
        if length < 1:
            raise SplurgeRangeError(
                f"length must be >= 1, got {length}",
                details=f"Value {length} is below minimum allowed value 1"
            )
        
        if not isinstance(allowable_chars, str):
            raise SplurgeParameterError(
                f"allowable_chars must be a string, got {type(allowable_chars).__name__}",
                details=f"Expected string, received: {repr(allowable_chars)}"
            )
        
        if not allowable_chars:
            raise SplurgeParameterError(
                "allowable_chars must be a non-empty string",
                details="Empty strings are not allowed"
            )

        return "".join(
            [
                allowable_chars[
                    cls.as_int_range(0, len(allowable_chars) - 1, secure=secure)
                ]
                for _ in range(0, length)
            ]
        )

    @classmethod
    def as_variable_string(
        cls,
        lower: int,
        upper: int,
        allowable_chars: str,
        *,
        secure: bool | None = False
    ) -> str:
        """
        Generate a random string with length between lower and upper bounds.

        Args:
            lower (int): Minimum length (inclusive)
            upper (int): Maximum length (inclusive)
            allowable_chars (str): Characters to use in the random string
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            str: Random string with length between lower and upper

        Raises:
            ValueError: If lower < 0 or lower >= upper

        Example:
            >>> random_variable_string(3, 5, "abc")
            'abcba'
            >>> random_variable_string(5, 10, RandomHelperConstants.ALPHANUMERIC_CHARS)
            'aB3cD4eF'
        """
        if not isinstance(lower, int):
            raise SplurgeParameterError(
                f"lower must be an integer, got {type(lower).__name__}",
                details=f"Expected integer, received: {repr(lower)}"
            )
        
        if lower < 0:
            raise SplurgeRangeError(
                f"lower must be >= 0, got {lower}",
                details=f"Value {lower} is below minimum allowed value 0"
            )
        
        if lower >= upper:
            raise SplurgeRangeError(
                "lower must be < upper",
                details=f"Got lower={lower}, upper={upper}"
            )

        length: int = cls.as_int_range(lower, upper, secure=secure)

        return (
            cls.as_string(length, allowable_chars, secure=secure) if length > 0 else ""
        )

    @classmethod
    def as_alpha(
        cls,
        length: int,
        *,
        secure: bool | None = False
    ) -> str:
        """
        Generate a random string of letters.

        Args:
            length (int): Length of the string to generate
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            str: Random string of letters

        Example:
            >>> random_alpha(5)
            'aBcDe'
            >>> random_alpha(5, secure=True)  # Cryptographically secure
            'XyZab'
        """
        return cls.as_string(length, cls.ALPHA_CHARS, secure=secure)

    @classmethod
    def as_alphanumeric(
        cls,
        length: int,
        *,
        secure: bool | None = False
    ) -> str:
        """
        Generate a random alphanumeric string.

        Args:
            length (int): Length of the string to generate
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            str: Random alphanumeric string

        Example:
            >>> random_alphanumeric(5)
            'aB3cD'
            >>> random_alphanumeric(5, secure=True)  # Cryptographically secure
            'Xy4Za'
        """
        return cls.as_string(length, cls.ALPHANUMERIC_CHARS, secure=secure)

    @classmethod
    def as_numeric(
        cls,
        length: int,
        *,
        secure: bool | None = False
    ) -> str:
        """
        Generate a random numeric string.

        Args:
            length (int): Length of the string to generate
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            str: Random numeric string

        Example:
            >>> random_numeric(5)
            '12345'
            >>> random_numeric(5, secure=True)  # Cryptographically secure
            '98765'
        """
        return cls.as_string(length, cls.DIGITS, secure=secure)

    @classmethod
    def as_base58(
        cls,
        length: int,
        *,
        secure: bool | None = False
    ) -> str:
        """
        Generate a random Base58 string.

        Args:
            length (int): Length of the string to generate
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            str: Random Base58 string

        Example:
            >>> random_base58(5)
            '1aB2c'
            >>> random_base58(5, secure=True)  # Cryptographically secure
            '3xY4z'
        """
        return cls.as_string(length, cls.BASE58_CHARS, secure=secure)

    @classmethod
    def as_base58_like(
        cls,
        size: int,
        *,
        symbols: str = SYMBOLS,
        secure: bool | None = False
    ) -> str:
        """
        Generate a Base58-like string with guaranteed character diversity.
        
        Creates a string from BASE58_ALPHA, BASE58_DIGITS, and symbols that contains
        at least one alphabetic character, one digit, and (if symbols provided) one symbol.
        
        Args:
            size (int): Length of the string to generate (must be >= 1)
            symbols (str, optional): Symbol characters to include from cls.SYMBOLS. 
                Defaults to cls.SYMBOLS. If empty or None, no symbols will be required or used.
                All characters must be from the SYMBOLS constant.
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.
        
        Returns:
            str: Random Base58-like string with guaranteed character diversity
            
        Raises:
            ValueError: If size < 1, if size is too small to satisfy character requirements,
                or if symbols contains characters not in cls.SYMBOLS
            
        Example:
            >>> RandomHelper.as_base58_like(5)
            'A3!bC'  # Contains alpha, digit, and symbol
            >>> RandomHelper.as_base58_like(3, symbols="")
            'A3b'    # Contains alpha and digit, no symbols required
            >>> RandomHelper.as_base58_like(10, symbols="@#$", secure=True)
            'A3@bC4#dE'  # Secure generation with symbols from SYMBOLS constant
        """
        if not isinstance(size, int):
            raise SplurgeParameterError(
                f"size must be an integer, got {type(size).__name__}",
                details=f"Expected integer, received: {repr(size)}"
            )
        
        if size < 1:
            raise SplurgeRangeError(
                f"size must be >= 1, got {size}",
                details=f"Value {size} is below minimum allowed value 1"
            )
        
        # Validate symbols parameter
        if symbols:
            invalid_chars = set(symbols) - set(cls.SYMBOLS)
            if invalid_chars:
                details_parts = []
                details_parts.append(f"Received value: {repr(symbols)} (type: {type(symbols).__name__})")
                details_parts.append("Suggestions:")
                details_parts.append(f"  - Use only characters from SYMBOLS constant: {cls.SYMBOLS}")
                details_parts.append(f"  - Remove invalid characters: {''.join(sorted(invalid_chars))}")
                details = "\n".join(details_parts)
                raise SplurgeFormatError("Invalid characters in symbols parameter", details=details)
        
        # Determine required character types
        use_symbols = symbols and len(symbols) > 0
        min_required = 2 if not use_symbols else 3  # alpha + digit + optional symbol
        
        if size < min_required:
            message = "Size too small to guarantee character diversity"
            details = f"Need at least {min_required} characters to include alpha, digit"
            if use_symbols:
                details += ", and symbol"
            raise SplurgeRangeError(message, details=details)
        
        # Build character set
        char_set = cls.BASE58_ALPHA + cls.BASE58_DIGITS
        if use_symbols:
            char_set += symbols
        
        # Generate string with guaranteed diversity
        result = []
        
        # Add required characters
        alpha_idx = cls.as_int_range(0, len(cls.BASE58_ALPHA) - 1, secure=secure)
        result.append(cls.BASE58_ALPHA[alpha_idx])  # At least one alpha
        
        digit_idx = cls.as_int_range(0, len(cls.BASE58_DIGITS) - 1, secure=secure)
        result.append(cls.BASE58_DIGITS[digit_idx])  # At least one digit
        
        if use_symbols:
            if len(symbols) == 1:
                result.append(symbols[0])  # Only one symbol available
            else:
                symbol_idx = cls.as_int_range(0, len(symbols) - 1, secure=secure)
                result.append(symbols[symbol_idx])  # At least one symbol
        
        # Fill remaining positions randomly from full character set
        remaining = size - len(result)
        for _ in range(remaining):
            char_idx = cls.as_int_range(0, len(char_set) - 1, secure=secure)
            result.append(char_set[char_idx])
        
        # Shuffle to avoid predictable patterns (Fisher-Yates shuffle)
        for i in range(len(result) - 1, 0, -1):
            j = cls.as_int_range(0, i, secure=secure)
            result[i], result[j] = result[j], result[i]
        
        return ''.join(result)

    @classmethod
    def as_variable_base58(
        cls,
        lower: int,
        upper: int,
        *,
        secure: bool | None = False
    ) -> str:
        """
        Generate a random Base58 string with variable length.

        Args:
            lower (int): Minimum length (inclusive)
            upper (int): Maximum length (inclusive)
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            str: Random Base58 string with length between lower and upper

        Example:
            >>> random_variable_base58(3, 5)
            '1aB2'
            >>> random_variable_base58(3, 5, secure=True)  # Cryptographically secure
            '3xY4'
        """
        return cls.as_variable_string(lower, upper, cls.BASE58_CHARS, secure=secure)

    @classmethod
    def as_variable_alpha(
        cls,
        lower: int,
        upper: int,
        *,
        secure: bool | None = False
    ) -> str:
        """
        Generate a random alphabetic string with variable length.

        Args:
            lower (int): Minimum length (inclusive)
            upper (int): Maximum length (inclusive)
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            str: Random alphabetic string with length between lower and upper

        Example:
            >>> random_variable_alpha(3, 5)
            'aBc'
            >>> random_variable_alpha(3, 5, secure=True)  # Cryptographically secure
            'XyZ'
        """
        return cls.as_variable_string(lower, upper, cls.ALPHA_CHARS, secure=secure)

    @classmethod
    def as_variable_alphanumeric(
        cls,
        lower: int,
        upper: int,
        *,
        secure: bool | None = False
    ) -> str:
        """
        Generate a random alphanumeric string with variable length.

        Args:
            lower (int): Minimum length (inclusive)
            upper (int): Maximum length (inclusive)
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            str: Random alphanumeric string with length between lower and upper

        Example:
            >>> random_variable_alphanumeric(3, 5)
            'aB3'
            >>> random_variable_alphanumeric(3, 5, secure=True)  # Cryptographically secure
            'Xy4'
        """
        return cls.as_variable_string(
            lower, upper, cls.ALPHANUMERIC_CHARS, secure=secure
        )

    @classmethod
    def as_variable_numeric(
        cls,
        lower: int,
        upper: int,
        *,
        secure: bool | None = False
    ) -> str:
        """
        Generate a random numeric string with variable length.

        Args:
            lower (int): Minimum length (inclusive)
            upper (int): Maximum length (inclusive)
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            str: Random numeric string with length between lower and upper

        Example:
            >>> random_variable_numeric(3, 5)
            '123'
            >>> random_variable_numeric(3, 5, secure=True)  # Cryptographically secure
            '987'
        """
        return cls.as_variable_string(lower, upper, cls.DIGITS, secure=secure)

    @classmethod
    def as_bool(
        cls,
        *,
        secure: bool | None = False
    ) -> bool:
        """
        Generate a random boolean value.

        Args:
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            bool: Random boolean value

        Example:
            >>> random_bool()
            True
            >>> random_bool(secure=True)  # Cryptographically secure
            False
        """
        return cls.as_int_range(0, 1, secure=secure) == 1

    @classmethod
    def as_masked_string(
        cls,
        mask: str,
        *,
        secure: bool | None = False
    ) -> str:
        """
        Generate a random string based on a mask pattern.

        The mask can contain:
        - '#' for random digits (0-9)
        - '@' for random letters (a-z, A-Z)
        - Other characters are preserved as-is

        Args:
            mask (str): Pattern to generate random string from
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            str: Random string following the mask pattern

        Raises:
            ValueError: If mask is empty or contains no mask characters (# or @)

        Example:
            >>> RandomHelper.as_masked_string('###-@@@')
            '123-abc'
            >>> RandomHelper.as_masked_string('###-@@@', secure=True)  # Cryptographically secure
            '456-xyz'
        """
        if not mask or (mask.count("#") == 0 and mask.count("@") == 0):
            details_parts = []
            details_parts.append(f"Received value: {repr(mask)} (type: {type(mask).__name__})")
            details_parts.append("Expected: string containing # (digit) or @ (letter) placeholders")
            details_parts.append("Suggestions:")
            details_parts.append("  - Use # for digit placeholders")
            details_parts.append("  - Use @ for letter placeholders")
            details_parts.append("  - Example: '###-@@-###' generates '123-AB-456'")
            details = "\n".join(details_parts)
            raise SplurgeFormatError("Invalid mask format", details=details)

        digit_count: int = mask.count("#")
        digits: str = cls.as_numeric(digit_count, secure=secure)
        alpha_count: int = mask.count("@")
        alphas: str = cls.as_alpha(alpha_count, secure=False)
        value: str = mask

        if digit_count:
            for digit in digits:
                value = value.replace("#", digit, 1)

        if alpha_count:
            for alpha in alphas:
                value = value.replace("@", alpha, 1)

        return value

    @classmethod
    def as_sequenced_string(
        cls,
        count: int,
        digits: int,
        *,
        start: int = 0,
        prefix: str | None = None,
        suffix: str | None = None
    ) -> List[str]:
        """
        Generate a list of sequentially numbered strings.

        Args:
            count (int): Number of strings to generate
            digits (int): Number of digits in the sequence number (zero-padded)
            start (int, optional): Starting number. Defaults to 0.
            prefix (str, optional): Prefix for each string. Defaults to None.
            suffix (str, optional): Suffix for each string. Defaults to None.

        Returns:
            List[str]: List of sequentially numbered strings

        Raises:
            ValueError: If count < 1, digits < 1, start < 0, or sequence would exceed digit capacity

        Example:
            >>> RandomHelper.as_sequenced_string(3, 3, prefix='ID-')
            ['ID-000', 'ID-001', 'ID-002']
            >>> RandomHelper.as_sequenced_string(3, 3, start=100, prefix='ID-', suffix='-END')
            ['ID-100-END', 'ID-101-END', 'ID-102-END']
        """
        if not isinstance(count, int):
            raise SplurgeParameterError(
                f"count must be an integer, got {type(count).__name__}",
                details=f"Expected integer, received: {repr(count)}"
            )
        
        if count < 1:
            raise SplurgeRangeError(
                f"count must be >= 1, got {count}",
                details=f"Value {count} is below minimum allowed value 1"
            )
        
        if not isinstance(digits, int):
            raise SplurgeParameterError(
                f"digits must be an integer, got {type(digits).__name__}",
                details=f"Expected integer, received: {repr(digits)}"
            )
        
        if digits < 1:
            raise SplurgeRangeError(
                f"digits must be >= 1, got {digits}",
                details=f"Value {digits} is below minimum allowed value 1"
            )
        
        if not isinstance(start, int):
            raise SplurgeParameterError(
                f"start must be an integer, got {type(start).__name__}",
                details=f"Expected integer, received: {repr(start)}"
            )
        
        if start < 0:
            raise SplurgeRangeError(
                f"start must be >= 0, got {start}",
                details=f"Value {start} is below minimum allowed value 0"
            )

        max_value: int = 10**digits - 1
        if start + count > max_value:
            details_parts = []
            details_parts.append("Suggestions:")
            details_parts.append(f"  - Increase digits parameter (current: {digits})")
            details_parts.append(f"  - Reduce count parameter (current: {count})")
            details_parts.append(f"  - Reduce start parameter (current: {start})")
            details_parts.append(f"  - Maximum sequence value with {digits} digits: {max_value}")
            details = "\n".join(details_parts)
            raise SplurgeRangeError("Sequence parameters exceed digit capacity", details=details)

        prefix = prefix if prefix else ""
        suffix = suffix if suffix else ""
        values: List[str] = []

        for sequence in range(start, start + count):
            values.append(f"{prefix}{sequence:0{digits}}{suffix}")

        return values

    @classmethod
    def as_date(
        cls,
        lower_days: int,
        upper_days: int,
        *,
        base_date: date | None = None,
        secure: bool | None = False
    ) -> date:
        """
        Generate a random date between two days.

        Args:
            lower_days (int): Minimum number of days from today
            upper_days (int): Maximum number of days from today
            base_date (date, optional): Base date to use for generation. Defaults to None.
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            datetime.date: Random date between two days

        Example:
            >>> RandomHelper.as_date(0, 30)
            datetime.date(2025, 6, 16)
            >>> RandomHelper.as_date(0, 30, secure=True)  # Cryptographically secure
            datetime.date(2025, 7, 15)
        """
        return (base_date if base_date else date.today()) + timedelta(
            days=cls.as_int_range(lower_days, upper_days, secure=secure)
        )

    @classmethod
    def as_datetime(
        cls,
        lower_days: int,
        upper_days: int,
        *,
        base_date: datetime | None = None,
        secure: bool | None = False
    ) -> datetime:
        """
        Generate a random datetime between two days.

        Args:
            lower_days (int): Minimum number of days from today
            upper_days (int): Maximum number of days from today
            base_date (datetime, optional): Base date to use for generation. Defaults to None.
            secure (bool, optional): If True, uses cryptographically secure random generation.
                Defaults to False.

        Returns:
            datetime: Random datetime between two days, with random time component

        Example:
            >>> RandomHelper.as_datetime(0, 30)
            datetime.datetime(2025, 6, 16, 14, 30, 45)
            >>> RandomHelper.as_datetime(0, 30, secure=True)  # Cryptographically secure
            datetime.datetime(2025, 7, 15, 9, 15, 30)
        """
        base_date = base_date if base_date else datetime.now()

        days: int = cls.as_int_range(lower_days, upper_days, secure=secure)
        result: datetime = base_date + timedelta(days=days)

        hours: int = cls.as_int_range(0, 23, secure=secure)
        minutes: int = cls.as_int_range(0, 59, secure=secure)
        seconds: int = cls.as_int_range(0, 59, secure=secure)
        microseconds: int = cls.as_int_range(0, 999999, secure=secure)

        return result.replace(
            hour=hours, minute=minutes, second=seconds, microsecond=microseconds
        )
