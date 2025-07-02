"""
Random helper module providing secure and non-secure random number generation utilities.
This module offers functions for generating random integers, strings, booleans, and more,
with options for both cryptographically secure and non-secure random generation.

The module uses Python's built-in `secrets` module for secure generation and `random` module
for non-secure generation. All methods support both secure and non-secure modes via the
`secure` parameter.

Copyright (c) 2022 Jim Schilling.

Please keep this header.

This module is licensed under the MIT License.
"""

import random
import string
import sys
from datetime import date, datetime, timedelta
from secrets import randbits
from typing import List, Optional


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
    BASE58_CHARS: str = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    @staticmethod
    def as_bytes(
        size: int,
        *,
        secure: Optional[bool] = False
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
        secure: Optional[bool] = False
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
        secure: Optional[bool] = False
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
            raise ValueError("lower must be < upper")
        if lower < cls.INT64_MIN or upper > cls.INT64_MAX:
            raise ValueError("allowed range is -2**63+1 to 2**63-1")
        return int(cls.as_int(secure=secure) % (upper - lower + 1)) + lower

    @classmethod
    def as_float_range(
        cls,
        lower: float,
        upper: float
    ) -> float:
        """
        Generate a random float within a specified range.

        Args:
            lower (float): Lower bound (inclusive)
            upper (float): Upper bound (inclusive)

        Returns:
            float: Random float between lower and upper (inclusive)

        Raises:
            ValueError: If lower >= upper

        Example:
            >>> random_float_range(0.0, 1.0)
            0.56789
            >>> random_float_range(-1.0, 1.0)
            0.12345
        """
        if lower >= upper:
            raise ValueError("lower must be < upper")
        return random.uniform(lower, upper)

    @classmethod
    def as_string(
        cls,
        length: int,
        allowable_chars: str,
        *,
        secure: Optional[bool] = False
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
        if length < 1:
            raise ValueError("length must be > 0")
        if not allowable_chars:
            raise ValueError("allowable_chars must be at least 1 character")

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
        secure: Optional[bool] = False
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
        if lower < 0 or lower >= upper:
            raise ValueError("lower must be >= 0 and < upper")

        length: int = cls.as_int_range(lower, upper, secure=secure)

        return (
            cls.as_string(length, allowable_chars, secure=secure) if length > 0 else ""
        )

    @classmethod
    def as_alpha(
        cls,
        length: int,
        *,
        secure: Optional[bool] = False
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
        secure: Optional[bool] = False
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
        secure: Optional[bool] = False
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
        secure: Optional[bool] = False
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
    def as_variable_base58(
        cls,
        lower: int,
        upper: int,
        *,
        secure: Optional[bool] = False
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
        secure: Optional[bool] = False
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
        secure: Optional[bool] = False
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
        secure: Optional[bool] = False
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
        secure: Optional[bool] = False
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
        secure: Optional[bool] = False
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
            raise ValueError("mask must contain at least one mask char # or @")

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
        start: Optional[int] = 0,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None
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
        if count < 1:
            raise ValueError("count must be >= 1")
        if digits < 1:
            raise ValueError("digits must be >= 1")
        if start < 0:
            raise ValueError("start must be >= 0")

        max_value: int = 10**digits - 1
        if start + count > max_value:
            raise ValueError(
                f"digits not large enough to hold sequence value of {max_value}"
            )

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
        base_date: Optional[date] = None,
        secure: Optional[bool] = False
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
        base_date: Optional[datetime] = None,
        secure: Optional[bool] = False
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
