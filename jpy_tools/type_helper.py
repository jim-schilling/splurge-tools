"""
type_helper module - Provides utilities for type checking, conversion and inference

This module offers a comprehensive set of tools for:
- Type inference and validation
- Data type conversion
- String parsing and validation
- Collection type checking
- Value profiling and analysis

Copyright (c) 2023 Jim Schilling

Please preserve this header and all related material when sharing!

This software is licensed under the MIT License.
"""

import collections
import re
import typing
from datetime import date, datetime
from enum import Enum
from typing import Any, Iterable, Union


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


class String:
    """
    Utility class for string type checking and conversion operations.

    This class provides static methods for:
    - Type validation (is_*_like methods)
    - Type conversion (to_* methods)
    - Type inference
    - String format validation
    """

    @staticmethod
    def is_bool_like(value: Union[str, bool, None], trim: bool = True) -> bool:
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
            tmp_value = value.lower().strip() if trim else value.lower()
            if tmp_value in ["true", "false"]:
                return True

        return False

    @staticmethod
    def is_none_like(value: Any, trim: bool = True) -> bool:
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
            tmp_value = value.strip().lower() if trim else value.lower()
            if tmp_value in ["none", "null"]:
                return True

        return False

    @staticmethod
    def is_empty_like(value: Any, trim: bool = True) -> bool:
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

    @staticmethod
    def is_float_like(value: Union[str, float, None], trim: bool = True) -> bool:
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
            >>> String.is_float_like('1')     # False
        """
        if value is None:
            return False

        if isinstance(value, float):
            return True

        if not isinstance(value, str):
            return False

        return (
            re.match(r"""^[-+]?(\d+)?\.(\d+)?$""", value.strip() if trim else value)
            is not None
        )

    @staticmethod
    def is_int_like(value: Union[str, int, None], trim: bool = True) -> bool:
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

        if not isinstance(value, str):
            return False

        tmp_value = value.strip() if trim else value
        return re.match(r"""^[-+]?\d+$""", tmp_value) is not None

    @classmethod
    def is_numeric_like(
        cls, value: Union[str, float, int, None], trim: bool = True
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

        return cls.is_float_like(value, trim) or cls.is_int_like(value, trim)

    @classmethod
    def is_category_like(cls, value: Union[str, None], trim: bool = True) -> bool:
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

        return not cls.is_numeric_like(value, trim)

    @staticmethod
    def _is_date_like(value: str) -> bool:
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
        patterns = [
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

        for pattern in patterns:
            try:
                datetime.strptime(value, pattern)
                return True
            except ValueError:
                pass

        return False

    @classmethod
    def is_date_like(cls, value: Union[str, date, None], trim: bool = True) -> bool:
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

        if not isinstance(value, str):
            return False

        tmp_value = value.strip() if trim else value

        if re.match(
            r"""^\d{4}[-/.]?\d{2}[-/.]?\d{2}$""", tmp_value
        ) and cls._is_date_like(tmp_value):
            return True

        if re.match(
            r"""^\d{2}[-/.]?\d{2}[-/.]?\d{4}$""", tmp_value
        ) and cls._is_date_like(tmp_value):
            return True

        return False

    @staticmethod
    def _is_datetime_like(value: str) -> bool:
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
        patterns = [
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

        for pattern in patterns:
            try:
                datetime.strptime(value, pattern)
                return True
            except ValueError:
                pass

        return False

    @classmethod
    def is_datetime_like(
        cls, value: Union[str, datetime, None], trim: bool = True
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

        if not isinstance(value, str):
            return False

        tmp_value = value.strip() if trim else value

        if re.match(
            r"""^\d{4}[-/.]?\d{2}[-/.]?\d{2}[T]?\d{2}[:]?\d{2}([:]?\d{2}([.]?\d{5})?)?$""",
            tmp_value,
        ) and cls._is_datetime_like(tmp_value):
            return True

        if re.match(
            r"""^\d{2}[-/.]?\d{2}[-/.]?\d{4}[T]?\d{2}[:]?\d{2}([:]?\d{2}([.]?\d{5})?)?$""",
            tmp_value,
        ) and cls._is_datetime_like(tmp_value):
            return True

        return False

    @classmethod
    def to_bool(
        cls,
        value: Union[str, bool, None],
        default: Union[bool, None] = None,
        trim: bool = True,
    ) -> Union[bool, None]:
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

        if cls.is_bool_like(value, trim):
            tmp_value = value.lower().strip() if trim else value.lower()
            return tmp_value == "true"

        return default

    @classmethod
    def to_float(
        cls,
        value: Union[str, float, None],
        default: Union[float, None] = None,
        trim: bool = True,
    ) -> Union[float, None]:
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
        return float(value) if cls.is_float_like(value, trim) else default

    @classmethod
    def to_int(
        cls,
        value: Union[str, int, None],
        default: Union[int, None] = None,
        trim: bool = True,
    ) -> Union[int, None]:
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
        return int(value) if cls.is_int_like(value, trim) else default

    @classmethod
    def to_date(
        cls,
        value: Union[str, date, None],
        default: Union[date, None] = None,
        trim: bool = True,
    ) -> Union[date, None]:
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

        if not cls.is_date_like(value, trim):
            return default

        patterns = [
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

        dvalue = value.strip() if trim else value

        for pattern in patterns:
            try:
                tmp_value = datetime.strptime(dvalue, pattern)
                return tmp_value.date()
            except ValueError:
                pass

        return default

    @classmethod
    def to_datetime(
        cls,
        value: Union[str, datetime, None],
        default: Union[datetime, None] = None,
        trim: bool = True,
    ) -> Union[datetime, None]:
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

        if not cls.is_datetime_like(value, trim):
            return default

        patterns = [
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

        tmp_value = value.strip() if trim else value

        for pattern in patterns:
            try:
                tvalue = datetime.strptime(tmp_value, pattern)
                return tvalue
            except ValueError:
                pass

        return default

    @staticmethod
    def has_leading_zero(value: Union[str, None], trim: bool = True) -> bool:
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
        value: Union[str, bool, int, float, date, datetime, None],
        trim: bool = True,
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
        if cls.is_none_like(value, trim):
            return DataType.NONE

        if cls.is_bool_like(value, trim):
            return DataType.BOOLEAN

        if cls.is_datetime_like(value, trim):
            return DataType.DATETIME

        if cls.is_date_like(value, trim):
            return DataType.DATE

        if cls.is_int_like(value, trim):
            return DataType.INTEGER

        if cls.is_float_like(value, trim):
            return DataType.FLOAT

        if cls.is_empty_like(value, trim):
            return DataType.EMPTY

        return DataType.STRING

    @classmethod
    def infer_type_name(
        cls,
        value: Union[str, bool, int, float, date, datetime, None],
        trim: bool = True,
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
        return cls.infer_type(value, trim).name


def profile_values(values: Iterable, trim: bool = True) -> DataType:
    """
    Infer the most appropriate data type for a collection of values.

    This function analyzes a collection of values and determines the most
    appropriate data type that can represent all values in the collection.

    Args:
        values: Collection of values to analyze
        trim: Whether to trim whitespace before checking

    Returns:
        DataType enum value representing the inferred type

    Raises:
        ValueError: If values is not iterable

    Examples:
        >>> profile_values(['1', '2', '3'])           # DataType.INTEGER
        >>> profile_values(['1.1', '2.2', '3.3'])     # DataType.FLOAT
        >>> profile_values(['1', '2.2', 'abc'])       # DataType.MIXED
        >>> profile_values(['true', 'false'])         # DataType.BOOLEAN
    """
    types = {
        DataType.BOOLEAN.name: 0,
        DataType.DATE.name: 0,
        DataType.DATETIME.name: 0,
        DataType.INTEGER.name: 0,
        DataType.FLOAT.name: 0,
        DataType.STRING.name: 0,
        DataType.EMPTY.name: 0,
        DataType.NONE.name: 0,
    }

    if not is_iterable_not_string(values):
        raise ValueError("values must be iterable")

    count = 0

    for value in values:
        types[String.infer_type(value, trim).name] += 1
        count += 1

    if types[DataType.EMPTY.name] == count:
        return DataType.EMPTY

    if types[DataType.NONE.name] == count:
        return DataType.NONE

    if types[DataType.NONE.name] + types[DataType.EMPTY.name] == count:
        return DataType.NONE

    if types[DataType.BOOLEAN.name] + types[DataType.EMPTY.name] == count:
        return DataType.BOOLEAN

    if types[DataType.DATE.name] + types[DataType.EMPTY.name] == count:
        return DataType.DATE

    if types[DataType.DATETIME.name] + types[DataType.EMPTY.name] == count:
        return DataType.DATETIME

    if types[DataType.INTEGER.name] + types[DataType.EMPTY.name] == count:
        return DataType.INTEGER

    if (
        types[DataType.FLOAT.name]
        + types[DataType.INTEGER.name]
        + types[DataType.EMPTY.name]
        == count
    ):
        return DataType.FLOAT

    if types[DataType.STRING.name] + types[DataType.EMPTY.name] == count:
        return DataType.STRING

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
    if isinstance(value, (collections.abc.Iterable, typing.Iterable)):
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
