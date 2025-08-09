"""
type_helper module - Provides utilities for type checking, conversion and inference

This module offers a comprehensive set of tools for:
- Type inference and validation
- Data type conversion
- String parsing and validation
- Collection type checking
- Value profiling and analysis

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

from collections import abc
import re
import typing
from datetime import date, datetime, time
from enum import Enum
from typing import Any, Iterable


class DataType(Enum):
    """
    Enumeration of supported data types for type inference and conversion.

    This enum defines the core data types that can be inferred and converted:
    - STRING: Text data
    - INTEGER: Whole numbers
    - FLOAT: Decimal numbers
    - BOOLEAN: True/False values
    - DATE: Calendar dates
    - TIME: Time values
    - DATETIME: Combined date and time
    - MIXED: Multiple types in collection
    - EMPTY: Empty values
    - NONE: Null/None values
    """

    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    MIXED = "mixed"
    EMPTY = "empty"
    NONE = "none"


class TypeInference:
    """
    Type inference utility that implements the TypeInferenceProtocol.
    
    This class provides methods for inferring data types and converting values
    to their inferred types.
    """
    
    def can_infer(
        self,
        value: Any
    ) -> bool:
        """
        Check if the value can be inferred as a specific type.
        
        Args:
            value: The value to check
            
        Returns:
            True if the value can be inferred as a specific type, False otherwise
        """
        if not isinstance(value, str):
            return False
            
        inferred_type = String.infer_type(value)
        return inferred_type != DataType.STRING
    
    def infer_type(
        self,
        value: str
    ) -> DataType:
        """
        Infer the type of the given value.
        
        Args:
            value: The value to infer the type for
            
        Returns:
            The inferred DataType
        """
        return String.infer_type(value)
    
    def convert_value(
        self,
        value: Any
    ) -> Any:
        """
        Convert the value to its inferred type.
        
        Args:
            value: The value to convert
            
        Returns:
            The converted value in its inferred type
        """
        inferred_type = self.infer_type(value)
        
        if inferred_type == DataType.BOOLEAN:
            return String.to_bool(value)
        elif inferred_type == DataType.INTEGER:
            return String.to_int(value)
        elif inferred_type == DataType.FLOAT:
            return String.to_float(value)
        elif inferred_type == DataType.DATE:
            return String.to_date(value)
        elif inferred_type == DataType.TIME:
            return String.to_time(value)
        elif inferred_type == DataType.DATETIME:
            return String.to_datetime(value)
        elif inferred_type == DataType.NONE:
            return None
        elif inferred_type == DataType.EMPTY:
            return ""
        else:
            return value


class String:
    """
    Utility class for string type checking and conversion operations.

    This class provides static methods for:
    - Type validation (is_*_like methods)
    - Type conversion (to_* methods)
    - Type inference
    - String format validation
    """

    # Private class-level constants for datetime patterns
    _DATE_PATTERNS: list[str] = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%Y%m%d",
        "%Y-%d-%m",
        "%Y/%d/%m",
        "%Y.%d.%m",
        "%Y%d%m",
        "%m-%d-%Y",
        "%m/%d/%Y",
        "%m.%d.%Y",
        "%m%d%Y",
    ]

    _TIME_PATTERNS: list[str] = [
        "%H:%M:%S",
        "%H:%M:%S.%f",
        "%H:%M",
        "%H%M",
        "%H%M%S",
        "%I:%M:%S.%f %p",
        "%I:%M:%S %p",
        "%I:%M %p",
        "%I:%M:%S%p",
        "%I:%M%p",
    ]

    _DATETIME_PATTERNS: list[str] = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y/%m/%dT%H:%M:%S",
        "%Y.%m.%dT%H:%M:%S",
        "%Y%m%d%H%M%S",
        "%Y-%d-%mT%H:%M:%S",
        "%Y/%d/%mT%H:%M:%S",
        "%Y.%d.%mT%H:%M:%S",
        "%Y%d%m%H%M%S",
        "%m-%d-%YT%H:%M:%S",
        "%m/%d/%YT%H:%M:%S",
        "%m.%d.%YT%H:%M:%S",
        "%m%d%Y%H%M%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y/%m/%dT%H:%M:%S.%f",
        "%Y.%m.%dT%H:%M:%S.%f",
        "%Y%m%d%H%M%S%f",
        "%Y-%d-%mT%H:%M:%S.%f",
        "%Y/%d/%mT%H:%M:%S.%f",
        "%Y.%d.%mT%H:%M:%S.%f",
        "%Y%d%m%H%M%S%f",
        "%m-%d-%YT%H:%M:%S.%f",
        "%m/%d/%YT%H:%M:%S.%f",
        "%m.%d.%YT%H:%M:%S.%f",
        "%m%d%Y%H%M%S%f",
    ]

    # Private class-level constants for regex patterns
    _FLOAT_REGEX = re.compile(r"""^[-+]?(\d+)?\.(\d+)?$""")
    _INTEGER_REGEX = re.compile(r"""^[-+]?\d+$""")
    _DATE_YYYY_MM_DD_REGEX = re.compile(r"""^\d{4}[-/.]?\d{2}[-/.]?\d{2}$""")
    _DATE_MM_DD_YYYY_REGEX = re.compile(r"""^\d{2}[-/.]?\d{2}[-/.]?\d{4}$""")
    _DATETIME_YYYY_MM_DD_REGEX = re.compile(
        r"""^\d{4}[-/.]?\d{2}[-/.]?\d{2}[T]?\d{2}[:]?\d{2}([:]?\d{2}([.]?\d{5})?)?$"""
    )
    _DATETIME_MM_DD_YYYY_REGEX = re.compile(
        r"""^\d{2}[-/.]?\d{2}[-/.]?\d{4}[T]?\d{2}[:]?\d{2}([:]?\d{2}([.]?\d{5})?)?$"""
    )
    _TIME_24HOUR_REGEX = re.compile(r"""^(\d{1,2}):(\d{2})(:(\d{2})([.](\d+))?)?$""")
    _TIME_12HOUR_REGEX = re.compile(r"""^(\d{1,2}):(\d{2})(:(\d{2})([.](\d+))?)?\s*(AM|PM|am|pm)$""")
    _TIME_COMPACT_REGEX = re.compile(r"""^(\d{2})(\d{2})(\d{2})?$""")

    @classmethod
    def is_bool_like(
        cls,
        value: str | bool | None,
        *,
        trim: bool = True
    ) -> bool:
        """
        Check if value can be interpreted as a boolean.

        Args:
            value: Value to check (string or bool)
            trim: Whether to trim whitespace before checking

        Returns:
            True if value is bool or string 'true'/'false'

        Examples:
            >>> String.is_bool_like('true')  # True
            >>> String.is_bool_like('false') # True
            >>> String.is_bool_like('yes')   # False
        """
        if isinstance(value, bool):
            return True

        if isinstance(value, str):
            tmp_value: str = value.lower().strip() if trim else value.lower()
            return tmp_value in ["true", "false"]

        return False

    @classmethod
    def is_none_like(
        cls,
        value: Any,
        *,
        trim: bool = True
    ) -> bool:
        """
        Check if value represents None/null.

        Args:
            value: Value to check
            trim: Whether to trim whitespace before checking

        Returns:
            True if value is None or string 'none'/'null'

        Examples:
            >>> String.is_none_like(None)    # True
            >>> String.is_none_like('none')  # True
            >>> String.is_none_like('null')  # True
        """
        if value is None:
            return True

        if isinstance(value, str):
            tmp_value: str = value.strip().lower() if trim else value.lower()
            return tmp_value in ["none", "null"]

        return False

    @classmethod
    def is_empty_like(
        cls,
        value: Any,
        *,
        trim: bool = True
    ) -> bool:
        """
        Check if value is an empty string or contains only whitespace.

        Args:
            value: Value to check
            trim: Whether to trim whitespace before checking

        Returns:
            True if value is empty string or contains only whitespace

        Examples:
            >>> String.is_empty_like('')      # True
            >>> String.is_empty_like('   ')   # True
            >>> String.is_empty_like('abc')   # False
            >>> String.is_empty_like(None)    # False
        """
        if not isinstance(value, str):
            return False

        return not value.strip() if trim else not value

    @classmethod
    def is_float_like(
        cls,
        value: str | float | None,
        *,
        trim: bool = True
    ) -> bool:
        """
        Check if value can be interpreted as a float.

        Args:
            value: Value to check (string or float)
            trim: Whether to trim whitespace before checking

        Returns:
            True if value is float or string representing a float

        Examples:
            >>> String.is_float_like('1.23')  # True
            >>> String.is_float_like('-1.23') # True
            >>> String.is_float_like('1')     # True
        """
        if value is None:
            return False

        if isinstance(value, float):
            return True

        if isinstance(value, str):
            return (
                cls._FLOAT_REGEX.match(value.strip() if trim else value)
                is not None
            )
        
        return False

    @classmethod
    def is_int_like(
        cls,
        value: str | int | None,
        *,
        trim: bool = True
    ) -> bool:
        """
        Check if value can be interpreted as an integer.

        Args:
            value: Value to check (string or int)
            trim: Whether to trim whitespace before checking

        Returns:
            True if value is int or string representing an integer

        Examples:
            >>> String.is_int_like('123')   # True
            >>> String.is_int_like('-123')  # True
            >>> String.is_int_like('1.23')  # False
        """
        if value is None:
            return False

        if isinstance(value, int):
            return True

        if isinstance(value, str):
            tmp_value: str = value.strip() if trim else value
            return cls._INTEGER_REGEX.match(tmp_value) is not None
        
        return False

    @classmethod
    def is_numeric_like(
        cls,
        value: str | float | int | None,
        *,
        trim: bool = True
    ) -> bool:
        """
        Check if value can be interpreted as a number (int or float).

        Args:
            value: Value to check (string, float, or int)
            trim: Whether to trim whitespace before checking

        Returns:
            True if value is numeric or string representing a number

        Examples:
            >>> String.is_numeric_like('123')   # True
            >>> String.is_numeric_like('1.23')  # True
            >>> String.is_numeric_like('abc')   # False
        """
        if value is None:
            return False

        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            return cls.is_float_like(value, trim=trim) or cls.is_int_like(value, trim=trim)
        return False

    @classmethod
    def is_category_like(
        cls,
        value: str | None,
        *,
        trim: bool = True
    ) -> bool:
        """
        Check if value is non-numeric (categorical).

        Args:
            value: Value to check
            trim: Whether to trim whitespace before checking

        Returns:
            True if value is not numeric

        Examples:
            >>> String.is_category_like('abc')   # True
            >>> String.is_category_like('123')   # False
            >>> String.is_category_like('1.23')  # False
        """
        if value is None:
            return False

        return not cls.is_numeric_like(value, trim=trim)

    @classmethod
    def _is_date_like(cls, value: str) -> bool:
        """
        Internal method to check if string matches common date formats.

        Args:
            value: String to check

        Returns:
            True if string matches a supported date format

        Note:
            Supports multiple date formats including:
            - YYYY-MM-DD
            - YYYY/MM/DD
            - YYYY.MM.DD
            - YYYYMMDD
            And their variations with different date component orders
        """
        for pattern in cls._DATE_PATTERNS:
            try:
                datetime.strptime(value, pattern)
                return True
            except ValueError:
                pass

        return False

    @classmethod
    def _is_time_like(cls, value: str) -> bool:
        """
        Internal method to check if string matches common time formats.

        Args:
            value: String to check

        Returns:
            True if string matches a supported time format

        Note:
            Supports multiple time formats including:
            - HH:MM:SS
            - HH:MM:SS.microseconds
            - HH:MM
            - HHMMSS
            - HHMM
            And 12-hour format variations with AM/PM
        """
        for pattern in cls._TIME_PATTERNS:
            try:
                datetime.strptime(value, pattern)
                return True
            except ValueError:
                pass

        return False

    @classmethod
    def is_date_like(
        cls,
        value: str | date | None,
        *,
        trim: bool = True
    ) -> bool:
        """
        Check if value can be interpreted as a date.

        Args:
            value: Value to check (string or date)
            trim: Whether to trim whitespace before checking

        Returns:
            True if value is date or string in supported date format

        Examples:
            >>> String.is_date_like('2023-01-01')  # True
            >>> String.is_date_like('01/01/2023')  # True
            >>> String.is_date_like('20230101')    # True
        """
        if not value:
            return False

        if isinstance(value, date):
            return True

        if isinstance(value, str):
            tmp_value: str = value.strip() if trim else value

            if String._DATE_YYYY_MM_DD_REGEX.match(tmp_value) and cls._is_date_like(tmp_value):
                return True

            if String._DATE_MM_DD_YYYY_REGEX.match(tmp_value) and cls._is_date_like(tmp_value):
                return True

        return False

    @classmethod
    def _is_datetime_like(cls, value: str) -> bool:
        """
        Internal method to check if string matches common datetime formats.

        Args:
            value: String to check

        Returns:
            True if string matches a supported datetime format

        Note:
            Supports multiple datetime formats including:
            - YYYY-MM-DDTHH:MM:SS
            - YYYY/MM/DDTHH:MM:SS
            - YYYY.MM.DDTHH:MM:SS
            - YYYYMMDDHHMMSS
            And their variations with different date component orders and optional microseconds
        """
        for pattern in cls._DATETIME_PATTERNS:
            try:
                datetime.strptime(value, pattern)
                return True
            except ValueError:
                pass

        return False

    @classmethod
    def is_datetime_like(
        cls,
        value: str | datetime | None,
        *,
        trim: bool = True
    ) -> bool:
        """
        Check if value can be interpreted as a datetime.

        Args:
            value: Value to check (string or datetime)
            trim: Whether to trim whitespace before checking

        Returns:
            True if value is datetime or string in supported datetime format

        Examples:
            >>> String.is_datetime_like('2023-01-01T12:00:00')     # True
            >>> String.is_datetime_like('2023-01-01T12:00:00.123') # True
            >>> String.is_datetime_like('2023-01-01')              # False
        """
        if not value:
            return False

        if isinstance(value, datetime):
            return True

        if isinstance(value, str):
            tmp_value: str = value.strip() if trim else value

            if String._DATETIME_YYYY_MM_DD_REGEX.match(tmp_value) and cls._is_datetime_like(tmp_value):
                return True

            if String._DATETIME_MM_DD_YYYY_REGEX.match(tmp_value) and cls._is_datetime_like(tmp_value):
                return True

        return False

    @classmethod
    def is_time_like(
        cls,
        value: str | time | None,
        *,
        trim: bool = True
    ) -> bool:
        """
        Check if value can be interpreted as a time.

        Args:
            value: Value to check (string or time)
            trim: Whether to trim whitespace before checking

        Returns:
            True if value is time or string in supported time format

        Examples:
            >>> String.is_time_like('14:30:00')     # True
            >>> String.is_time_like('14:30:00.123') # True
            >>> String.is_time_like('2:30 PM')      # True
            >>> String.is_time_like('143000')       # True
            >>> String.is_time_like('2023-01-01')   # False
        """
        if not value:
            return False

        if isinstance(value, time):
            return True

        if isinstance(value, str):
            tmp_value: str = value.strip() if trim else value

            if String._TIME_24HOUR_REGEX.match(tmp_value) and cls._is_time_like(tmp_value):
                return True

            if String._TIME_12HOUR_REGEX.match(tmp_value) and cls._is_time_like(tmp_value):
                return True

            if String._TIME_COMPACT_REGEX.match(tmp_value) and cls._is_time_like(tmp_value):
                return True

        return False

    @classmethod
    def to_bool(
        cls,
        value: str | bool | None,
        *,
        default: bool | None = None,
        trim: bool = True
    ) -> bool | None:
        """
        Convert value to boolean.

        Args:
            value: Value to convert
            default: Default value if conversion fails
            trim: Whether to trim whitespace before converting

        Returns:
            Boolean value or default if conversion fails

        Examples:
            >>> String.to_bool('true')   # True
            >>> String.to_bool('false')  # False
            >>> String.to_bool('yes')    # None
        """
        if isinstance(value, bool):
            return value

        if cls.is_bool_like(value, trim=trim):
            if isinstance(value, str):
                tmp_value: str = value.lower().strip() if trim else value.lower()
                return tmp_value == "true"

        return default

    @classmethod
    def to_float(
        cls,
        value: str | float | None,
        *,
        default: float | None = None,
        trim: bool = True
    ) -> float | None:
        """
        Convert value to float.

        Args:
            value: Value to convert
            default: Default value if conversion fails
            trim: Whether to trim whitespace before converting

        Returns:
            Float value or default if conversion fails

        Examples:
            >>> String.to_float('1.23')  # 1.23
            >>> String.to_float('-1.23') # -1.23
            >>> String.to_float('abc')   # None
        """
        if cls.is_float_like(value, trim=trim) and value is not None:
            return float(value)
        return default

    @classmethod
    def to_int(
        cls,
        value: str | int | None,
        *,
        default: int | None = None,
        trim: bool = True
    ) -> int | None:
        """
        Convert value to integer.

        Args:
            value: Value to convert
            default: Default value if conversion fails
            trim: Whether to trim whitespace before converting

        Returns:
            Integer value or default if conversion fails

        Examples:
            >>> String.to_int('123')   # 123
            >>> String.to_int('-123')  # -123
            >>> String.to_int('1.23')  # None
        """
        if cls.is_int_like(value, trim=trim) and value is not None:
            return int(value)
        return default

    @classmethod
    def to_date(
        cls,
        value: str | date | None,
        *,
        default: date | None = None,
        trim: bool = True
    ) -> date | None:
        """
        Convert value to date.

        Args:
            value: Value to convert
            default: Default value if conversion fails
            trim: Whether to trim whitespace before converting

        Returns:
            Date value or default if conversion fails

        Examples:
            >>> String.to_date('2023-01-01')  # datetime.date(2023, 1, 1)
            >>> String.to_date('01/01/2023')  # datetime.date(2023, 1, 1)
            >>> String.to_date('invalid')     # None
        """
        if isinstance(value, date):
            return value

        if not cls.is_date_like(value, trim=trim):
            return default

        if not isinstance(value, str):
            return default
            
        dvalue: str = value.strip() if trim else value

        for pattern in cls._DATE_PATTERNS:
            try:
                tmp_value = datetime.strptime(dvalue, pattern)
                return tmp_value.date()
            except ValueError:
                pass

        return default

    @classmethod
    def to_datetime(
        cls,
        value: str | datetime | None,
        *,
        default: datetime | None = None,
        trim: bool = True
    ) -> datetime | None:
        """
        Convert value to datetime.

        Args:
            value: Value to convert
            default: Default value if conversion fails
            trim: Whether to trim whitespace before converting

        Returns:
            Datetime value or default if conversion fails

        Examples:
            >>> String.to_datetime('2023-01-01T12:00:00')     # datetime(2023, 1, 1, 12, 0)
            >>> String.to_datetime('2023-01-01T12:00:00.123') # datetime(2023, 1, 1, 12, 0, 0, 123000)
            >>> String.to_datetime('invalid')                 # None
        """
        if isinstance(value, datetime):
            return value

        if not cls.is_datetime_like(value, trim=trim):
            return default

        if not isinstance(value, str):
            return default
            
        tmp_value: str = value.strip() if trim else value

        for pattern in cls._DATETIME_PATTERNS:
            try:
                tvalue = datetime.strptime(tmp_value, pattern)
                return tvalue
            except ValueError:
                pass

        return default

    @classmethod
    def to_time(
        cls,
        value: str | time | None,
        *,
        default: time | None = None,
        trim: bool = True
    ) -> time | None:
        """
        Convert value to time.

        Args:
            value: Value to convert
            default: Default value if conversion fails
            trim: Whether to trim whitespace before converting

        Returns:
            Time value or default if conversion fails

        Examples:
            >>> String.to_time('14:30:00')     # datetime.time(14, 30)
            >>> String.to_time('2:30 PM')      # datetime.time(14, 30)
            >>> String.to_time('143000')       # datetime.time(14, 30, 0)
            >>> String.to_time('invalid')      # None
        """
        if isinstance(value, time):
            return value

        if not cls.is_time_like(value, trim=trim):
            return default

        if not isinstance(value, str):
            return default
            
        tmp_value: str = value.strip() if trim else value

        for pattern in cls._TIME_PATTERNS:
            try:
                tvalue = datetime.strptime(tmp_value, pattern)
                return tvalue.time()
            except ValueError:
                pass

        return default

    @classmethod
    def has_leading_zero(
        cls,
        value: str | None,
        *,
        trim: bool = True
    ) -> bool:
        """
        Check if string value has leading zero.

        Args:
            value: Value to check
            trim: Whether to trim whitespace before checking

        Returns:
            True if value starts with '0'

        Examples:
            >>> String.has_leading_zero('01')    # True
            >>> String.has_leading_zero('10')    # False
            >>> String.has_leading_zero(' 01')   # True (with trim=True)
        """
        if value is None:
            return False

        return value.strip().startswith("0") if trim else value.startswith("0")

    @classmethod
    def infer_type(
        cls,
        value: str | bool | int | float | date | time | datetime | None,
        *,
        trim: bool = True
    ) -> DataType:
        """
        Infer the most appropriate data type for a value.

        Args:
            value: Value to check
            trim: Whether to trim whitespace before checking

        Returns:
            DataType enum value representing the inferred type

        Examples:
            >>> String.infer_type('123')           # DataType.INTEGER
            >>> String.infer_type('1.23')          # DataType.FLOAT
            >>> String.infer_type('2023-01-01')    # DataType.DATE
            >>> String.infer_type('true')          # DataType.BOOLEAN
            >>> String.infer_type('abc')           # DataType.STRING
        """
        # Handle non-string types first
        if isinstance(value, bool):
            return DataType.BOOLEAN
        elif isinstance(value, int):
            return DataType.INTEGER
        elif isinstance(value, float):
            return DataType.FLOAT
        elif isinstance(value, datetime):
            return DataType.DATETIME
        elif isinstance(value, time):
            return DataType.TIME
        elif isinstance(value, date):
            return DataType.DATE
        
        # Handle string and None types
        if cls.is_none_like(value, trim=trim):
            return DataType.NONE

        if cls.is_empty_like(value, trim=trim):
            return DataType.EMPTY

        if isinstance(value, str):
            if cls.is_bool_like(value, trim=trim):
                return DataType.BOOLEAN

            if cls.is_datetime_like(value, trim=trim):
                return DataType.DATETIME

            if cls.is_time_like(value, trim=trim):
                return DataType.TIME

            if cls.is_date_like(value, trim=trim):
                return DataType.DATE

            if cls.is_int_like(value, trim=trim):
                return DataType.INTEGER

            if cls.is_float_like(value, trim=trim):
                return DataType.FLOAT

        return DataType.STRING

    @classmethod
    def infer_type_name(
        cls,
        value: str | bool | int | float | date | time | datetime | None,
        *,
        trim: bool = True
    ) -> str:
        """
        Infer the most appropriate data type name for a value.

        Args:
            value: Value to check
            trim: Whether to trim whitespace before checking

        Returns:
            String name of the inferred type

        Examples:
            >>> String.infer_type_name('123')           # 'INTEGER'
            >>> String.infer_type_name('1.23')          # 'FLOAT'
            >>> String.infer_type_name('2023-01-01')    # 'DATE'
            >>> String.infer_type_name('true')          # 'BOOLEAN'
            >>> String.infer_type_name('abc')           # 'STRING'
        """
        return cls.infer_type(value, trim=trim).name


def _determine_type_from_counts(
    types: dict[str, int],
    count: int,
    *,
    allow_special_cases: bool = True
) -> DataType | None:
    """
    Determine the data type based on type counts.
    
    Args:
        types: Dictionary of type counts
        count: Total number of values processed
        allow_special_cases: Whether to apply special case logic (all-digit strings, etc.)
    
    Returns:
        DataType if a definitive type can be determined, None otherwise
    """
    if types[DataType.EMPTY.name] == count:
        return DataType.EMPTY

    if types[DataType.NONE.name] == count:
        return DataType.NONE

    if types[DataType.NONE.name] + types[DataType.EMPTY.name] == count:
        return DataType.NONE

    if types[DataType.BOOLEAN.name] + types[DataType.EMPTY.name] == count:
        return DataType.BOOLEAN

    if types[DataType.STRING.name] + types[DataType.EMPTY.name] == count:
        return DataType.STRING

    # For early termination, skip complex logic that requires full analysis
    if not allow_special_cases:
        return None

    if types[DataType.DATE.name] + types[DataType.EMPTY.name] == count:
        return DataType.DATE

    if types[DataType.DATETIME.name] + types[DataType.EMPTY.name] == count:
        return DataType.DATETIME

    if types[DataType.TIME.name] + types[DataType.EMPTY.name] == count:
        return DataType.TIME

    if types[DataType.INTEGER.name] + types[DataType.EMPTY.name] == count:
        return DataType.INTEGER

    if (
        types[DataType.FLOAT.name]
        + types[DataType.INTEGER.name]
        + types[DataType.EMPTY.name]
        == count
    ):
        return DataType.FLOAT

    return None


_INCREMENTAL_TYPECHECK_THRESHOLD = 10_000

def profile_values(
    values: Iterable[Any], 
    *, 
    trim: bool = True,
    use_incremental_typecheck: bool = True
) -> DataType:
    """
    Infer the most appropriate data type for a collection of values.

    This function analyzes a collection of values and determines the most
    appropriate data type that can represent all values in the collection.
    For lists of more than _INCREMENTAL_TYPECHECK_THRESHOLD items, it uses weighted incremental checks
    to short-circuit early when enough information is available to determine
    the final data type. For lists of _INCREMENTAL_TYPECHECK_THRESHOLD or fewer items, incremental
    type checking is disabled and a single pass is used.

    Args:
        values: Collection of values to analyze
        trim: Whether to trim whitespace before checking
        use_incremental_typecheck: Whether to use incremental type checking for early termination.
                                  For lists of _INCREMENTAL_TYPECHECK_THRESHOLD or fewer items, this is always False.

    Returns:
        DataType enum value representing the inferred type

    Raises:
        ValueError: If values is not iterable

    Examples:
        >>> profile_values(['1', '2', '3'])           # DataType.INTEGER
        >>> profile_values(['1.1', '2.2', '3.3'])     # DataType.FLOAT
        >>> profile_values(['1', '2.2', 'abc'])       # DataType.MIXED
        >>> profile_values(['true', 'false'])         # DataType.BOOLEAN
        >>> profile_values(['1', '2', '3'], use_incremental_typecheck=False)  # Full analysis
    """
    if not is_iterable_not_string(values):
        raise ValueError("values must be iterable")

    # Convert to list to handle generators and ensure we can iterate multiple times
    values_list: list[Any] = list(values)
    
    if not values_list:
        return DataType.EMPTY
    
    # Only enable incremental type checking for lists larger than the threshold
    if len(values_list) <= _INCREMENTAL_TYPECHECK_THRESHOLD:
        use_incremental_typecheck = False
    
    # Sequential processing with incremental checks
    types = {
        DataType.BOOLEAN.name: 0,
        DataType.DATE.name: 0,
        DataType.TIME.name: 0,
        DataType.DATETIME.name: 0,
        DataType.INTEGER.name: 0,
        DataType.FLOAT.name: 0,
        DataType.STRING.name: 0,
        DataType.EMPTY.name: 0,
        DataType.NONE.name: 0,
    }

    count = 0
    total_count = len(values_list)
    
    # Check points for early termination (25%, 50%, 75%) - only used if incremental checking is enabled
    check_points = {}
    if use_incremental_typecheck:
        check_points = {
            int(total_count * 0.25): False,
            int(total_count * 0.50): False,
            int(total_count * 0.75): False,
        }

    # First pass: count types with incremental checks
    for value in values_list:
        inferred_type = String.infer_type(value, trim=trim)
        types[inferred_type.name] += 1
        count += 1
        
        # Check for early termination at check points (only if incremental checking is enabled)
        if use_incremental_typecheck and count in check_points:
            # Only do early termination for very clear cases that don't involve
            # the special all-digit string logic or mixed int/float detection
            
            # Early detection of MIXED type: if we have both numeric/temporal types AND string types
            numeric_temporal_count = (
                types[DataType.INTEGER.name] + 
                types[DataType.FLOAT.name] + 
                types[DataType.DATE.name] + 
                types[DataType.DATETIME.name] + 
                types[DataType.TIME.name]
            )
            string_count = types[DataType.STRING.name]
            
            if numeric_temporal_count > 0 and string_count > 0:
                return DataType.MIXED
            
            early_result = _determine_type_from_counts(types, count, allow_special_cases=False)
            if early_result is not None:
                return early_result

    # Final determination based on complete analysis
    final_result = _determine_type_from_counts(types, count, allow_special_cases=True)
    if final_result is not None:
        return final_result

    # Special case: if we have mixed DATE, TIME, DATETIME, INTEGER types,
    # check if all values are all-digit strings and prioritize INTEGER
    if (types[DataType.DATE.name] + types[DataType.TIME.name] + 
        types[DataType.DATETIME.name] + types[DataType.INTEGER.name] + 
        types[DataType.EMPTY.name] == count and
        (types[DataType.DATE.name] > 0 or types[DataType.TIME.name] > 0 or 
         types[DataType.DATETIME.name] > 0 or types[DataType.EMPTY.name] > 0)):
        
        # Second pass: check if all non-empty values are all-digit strings (with optional +/- signs)
        all_digit_values = True
        for value in values_list:
            if not String.is_empty_like(value, trim=trim) and not String.is_int_like(value, trim=trim):
                all_digit_values = False
                break
        
        if all_digit_values:
            return DataType.INTEGER

    return DataType.MIXED


def is_list_like(value: Any) -> bool:
    """
    Check if value behaves like a list.

    Args:
        value: Value to check

    Returns:
        True if value is a list or has list-like behavior (has append, remove, index methods)

    Examples:
        >>> is_list_like([1, 2, 3])        # True
        >>> is_list_like((1, 2, 3))        # False
        >>> is_list_like('abc')            # False
    """
    if isinstance(value, list):
        return True

    if (
        hasattr(value, "__iter__")
        and hasattr(value, "append")
        and hasattr(value, "remove")
        and hasattr(value, "index")
    ):
        return True

    return False


def is_dict_like(value: Any) -> bool:
    """
    Check if value behaves like a dictionary.

    Args:
        value: Value to check

    Returns:
        True if value is a dict or has dict-like behavior (has keys, get, values methods)

    Examples:
        >>> is_dict_like({'a': 1})         # True
        >>> is_dict_like([1, 2, 3])        # False
        >>> is_dict_like('abc')            # False
    """
    if isinstance(value, dict):
        return True

    if hasattr(value, "keys") and hasattr(value, "get") and hasattr(value, "values"):
        return True

    return False


def is_iterable(value: Any) -> bool:
    """
    Check if value is iterable.

    Args:
        value: Value to check

    Returns:
        True if value is iterable (has __iter__, __getitem__, __len__, __next__ methods)

    Examples:
        >>> is_iterable([1, 2, 3])         # True
        >>> is_iterable((1, 2, 3))         # True
        >>> is_iterable('abc')             # True
        >>> is_iterable(123)               # False
    """
    if isinstance(value, (abc.Iterable, typing.Iterable)):
        return True

    if (
        hasattr(value, "__iter__")
        and hasattr(value, "__getitem__")
        and hasattr(value, "__len__")
        and hasattr(value, "__next__")
    ):
        return True

    return False


def is_iterable_not_string(value: Any) -> bool:
    """
    Check if value is iterable but not a string.

    Args:
        value: Value to check

    Returns:
        True if value is iterable and not a string

    Examples:
        >>> is_iterable_not_string([1, 2, 3])  # True
        >>> is_iterable_not_string((1, 2, 3))  # True
        >>> is_iterable_not_string('abc')      # False
        >>> is_iterable_not_string(123)        # False
    """
    if not isinstance(value, str) and is_iterable(value):
        return True

    return False


def is_empty(value: Any) -> bool:
    """
    Check if value is empty.

    Args:
        value: Value to check

    Returns:
        True if value is empty (None, empty string, empty collection)

    Examples:
        >>> is_empty(None)           # True
        >>> is_empty('')             # True
        >>> is_empty('   ')          # True
        >>> is_empty([])             # True
        >>> is_empty({})             # True
        >>> is_empty('abc')          # False
        >>> is_empty([1, 2, 3])      # False
    """
    if value is None:
        return True

    if isinstance(value, str) and not value.strip():
        return True

    if isinstance(value, (list, tuple, set)) and not value:
        return True

    if isinstance(value, dict) and not value:
        return True

    return False
