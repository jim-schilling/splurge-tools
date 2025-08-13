"""
Tabular data model classes for structured data operations.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import re
import warnings
from typing import Generator, Iterator, Any

from splurge_tools.protocols import TabularDataProtocol
from splurge_tools.type_helper import DataType, profile_values
from splurge_tools.validation_utils import Validator
from splurge_tools.tabular_utils import process_headers as _process_headers, normalize_rows as _normalize_rows
from splurge_tools.common_utils import validate_data_structure, safe_dict_access, safe_index_access
from splurge_tools.exceptions import SplurgeParameterError, SplurgeRangeError


class TabularDataModel(TabularDataProtocol):
    """
    Tabular data model for structured data.
    
    This class implements the TabularDataProtocol interface, providing
    a consistent interface for tabular data operations.
    """

    def __init__(
        self,
        data: list[list[str]],
        *,
        header_rows: int = 1,
        skip_empty_rows: bool = True
    ) -> None:
        """
        Initialize TabularDataModel.

        Args:
            data (list[list[str]]): Raw data rows.
            header_rows (int): Number of header rows to merge into column names.
            skip_empty_rows (bool): Skip empty rows in data.

        Raises:
            ValueError: If data or header configuration is invalid.
        """
        data = validate_data_structure(data, expected_type=list, param_name="data", allow_empty=False)
        header_rows = Validator.is_non_negative_integer(header_rows, "header_rows")

        self._raw_data = data
        self._header_rows = header_rows
        self._header_data = data[:header_rows] if header_rows > 0 else []
        self._data = (
            self._normalize_data_model(data[header_rows:], skip_empty_rows)
            if header_rows > 0
            else self._normalize_data_model(data, skip_empty_rows)
        )
        self._header_columns = len(self._header_data[0]) if len(self._header_data) > 0 else 0
        self._columns = len(self._data[0]) if len(self._data) > 0 else 0
        self._rows = len(self._data) if len(self._data) > 0 else 0

        # Process headers using shared utility
        self._header_data, self._column_names = _process_headers(
            self._header_data,
            header_rows=header_rows
        )
        
        # Ensure column names match the actual column count
        while len(self._column_names) < self._columns:
            self._column_names.append(f"column_{len(self._column_names)}")
        self._column_index_map = {name: i for i, name in enumerate(self._column_names)}
        self._column_types: dict[str, DataType] = {}

    # Removed local process_headers; logic is shared in splurge_tools.tabular_utils

    @property
    def column_names(self) -> list[str]:
        """
        List of column names.
        """
        return self._column_names

    def column_index(
        self,
        name: str
    ) -> int:
        """
        Get the column index for a given name.

        Args:
            name (str): Column name.

        Returns:
            int: Column index.

        Raises:
            ValueError: If column name is not found.
        """
        return safe_dict_access(self._column_index_map, name, item_name="column")

    @property
    def row_count(self) -> int:
        """
        Number of rows.
        """
        return self._rows

    @property
    def column_count(self) -> int:
        """
        Number of columns.
        """
        return self._columns

    def column_type(
        self,
        name: str
    ) -> DataType:
        """
        Get the inferred data type for a column (cached).

        Args:
            name (str): Column name.

        Returns:
            DataType: Inferred data type.

        Raises:
            ValueError: If column name is not found.
        """
        safe_dict_access(self._column_index_map, name, item_name="column")
        if name not in self._column_types:
            col_idx: int = self._column_index_map[name]
            values: list[str] = [row[col_idx] for row in self._data]
            self._column_types[name] = profile_values(values)
        return self._column_types[name]

    def column_values(
        self,
        name: str
    ) -> list[str]:
        """
        Get all values for a column.

        Args:
            name (str): Column name.

        Returns:
            list[str]: Values in the column.

        Raises:
            ValueError: If column name is not found.
        """
        safe_dict_access(self._column_index_map, name, item_name="column")
        col_idx: int = self._column_index_map[name]
        return [row[col_idx] for row in self._data]

    def cell_value(
        self,
        name: str,
        row_index: int
    ) -> str:
        """
        Get a cell value by column name and row index.

        Args:
            name (str): Column name.
            row_index (int): Row index (0-based).

        Returns:
            str: Cell value.

        Raises:
            ValueError: If column name is not found or row index is out of range.
        """
        safe_dict_access(self._column_index_map, name, item_name="column")
        if row_index < 0 or row_index >= self._rows:
            raise SplurgeRangeError(
                f"Row index {row_index} out of range",
                details=f"Valid range: 0 to {self._rows - 1}"
            )
        col_idx: int = self._column_index_map[name]
        return self._data[row_index][col_idx]

    def __iter__(self) -> Iterator[list[str]]:
        return iter(self._data)

    def iter_rows(self) -> Generator[dict[str, str], None, None]:
        """
        Iterate over rows as dictionaries.

        Yields:
            dict[str, str]: Row as a dictionary.
        """
        for row in self._data:
            yield dict(zip(self._column_names, row))

    def iter_rows_as_tuples(self) -> Generator[tuple[str, ...], None, None]:
        """
        Iterate over rows as tuples.

        Yields:
            tuple[str, ...]: Row as a tuple.
        """
        for row in self._data:
            yield tuple(row)

    def row(
        self,
        index: int
    ) -> dict[str, str]:
        """
        Get a row as a dictionary.

        Args:
            index (int): Row index (0-based).

        Returns:
            dict[str, str]: Row as a dictionary.
        """
        row_data = self._data[index]
        # Ensure row_data is properly padded to match column count
        padded_row = row_data + [""] * (self._columns - len(row_data))
        return {
            self._column_names[i]: padded_row[i]
            for i in range(self._columns)
        }

    def row_as_list(
        self,
        index: int
    ) -> list[str]:
        """
        Get a row as a list.

        Args:
            index (int): Row index (0-based).

        Returns:
            list[str]: Row as a list.
        """
        return self._data[index]

    def row_as_tuple(
        self,
        index: int
    ) -> tuple[str, ...]:
        """
        Get a row as a tuple.

        Args:
            index (int): Row index (0-based).

        Returns:
            tuple[str, ...]: Row as a tuple.
        """
        return tuple(self._data[index])

    def to_typed(
        self,
        *,
        type_configs: dict[DataType, Any] | None = None
    ) -> "_TypedView":
        """Return a typed view over this model.

        Args:
            type_configs: Optional overrides for default type conversion behavior.

        Returns:
            _TypedView: A lightweight wrapper that provides typed access.
        """
        return _TypedView(self, type_configs=type_configs)

    @staticmethod
    def _normalize_data_model(
        rows: list[list[str]],
        skip_empty_rows: bool = True
    ) -> list[list[str]]:
        """
        Normalize the data model (pad rows, optionally skip empty rows).

        Args:
            rows (list[list[str]]): Data rows.
            skip_empty_rows (bool): Skip empty rows if True.

        Returns:
            list[list[str]]: Normalized data rows.
        """
        return _normalize_rows(rows, skip_empty_rows=skip_empty_rows)


class _TypedView:
    """Lightweight typed access wrapper for TabularDataModel.

    Performs lazy per-cell conversions using the model's inferred column types.
    """

    def __init__(
        self,
        model: TabularDataModel,
        *,
        type_configs: dict[DataType, Any] | None = None
    ) -> None:
        from splurge_tools.type_helper import String  # local import to avoid cycles

        self._model = model
        self._string = String
        # Defaults mirror previous TypedTabularDataModel semantics (empty vs none)
        self._type_defaults: dict[DataType, dict[str, Any]] = {
            DataType.BOOLEAN: {"empty": False, "none": False},
            DataType.INTEGER: {"empty": 0, "none": 0},
            DataType.FLOAT: {"empty": 0.0, "none": 0.0},
            DataType.DATE: {"empty": None, "none": None},
            DataType.DATETIME: {"empty": None, "none": None},
            DataType.STRING: {"empty": "", "none": ""},
            DataType.MIXED: {"empty": "", "none": None},
            DataType.EMPTY: {"empty": "", "none": ""},
            DataType.NONE: {"empty": None, "none": None},
            DataType.TIME: {"empty": None, "none": None},
        }

        # Apply overrides using semantics expected by tests:
        # - BOOLEAN, MIXED: override none-default only
        # - Others (INTEGER, FLOAT, STRING, TIME, DATE, DATETIME, EMPTY, NONE): override empty-default only
        if type_configs:
            override_none: set[DataType] = {DataType.BOOLEAN, DataType.MIXED}
            for dt, override_value in type_configs.items():
                if dt not in self._type_defaults:
                    continue
                if dt in override_none:
                    self._type_defaults[dt]["none"] = override_value
                else:
                    self._type_defaults[dt]["empty"] = override_value

    @property
    def column_names(self) -> list[str]:
        return self._model.column_names

    @property
    def row_count(self) -> int:
        return self._model.row_count

    @property
    def column_count(self) -> int:
        return self._model.column_count

    def column_index(self, name: str) -> int:
        return self._model.column_index(name)

    def __iter__(self) -> Iterator[list[object]]:
        from splurge_tools.type_helper import String

        for row in self._model:
            yield [self._convert(value, self._inferred_type(i)) for i, value in enumerate(row)]

    def iter_rows(self) -> Generator[dict[str, object], None, None]:
        for row in self:
            yield dict(zip(self.column_names, row))

    def iter_rows_as_tuples(self) -> Generator[tuple[object, ...], None, None]:
        for row in self:
            yield tuple(row)

    def column_values(self, name: str) -> list[object]:
        from splurge_tools.exceptions import SplurgeParameterError

        try:
            col_idx = self._model.column_index(name)
        except SplurgeParameterError as e:
            raise ValueError(str(e))
        dtype = self._inferred_type(col_idx)
        return [self._convert(v, dtype) for v in self._model.column_values(name)]

    def cell_value(self, name: str, row_index: int) -> object:
        from splurge_tools.exceptions import SplurgeParameterError, SplurgeRangeError

        try:
            col_idx = self._model.column_index(name)
        except SplurgeParameterError as e:
            raise ValueError(str(e))
        dtype = self._inferred_type(col_idx)
        try:
            raw = self._model.cell_value(name, row_index)
        except SplurgeRangeError as e:
            raise ValueError(str(e))
        return self._convert(raw, dtype)

    def row(self, index: int) -> dict[str, object]:
        """Get a typed row as a dictionary."""
        typed_list = self.row_as_list(index)
        return {self.column_names[i]: typed_list[i] for i in range(self.column_count)}

    def row_as_list(self, index: int) -> list[object]:
        """Get a typed row as a list."""
        if index < 0 or index >= self._model.row_count:
            raise ValueError(f"Row index {index} out of range")
        raw = self._model.row_as_list(index)
        return [self._convert(val, self._inferred_type(i)) for i, val in enumerate(raw)]

    def row_as_tuple(self, index: int) -> tuple[object, ...]:
        """Get a typed row as a tuple."""
        return tuple(self.row_as_list(index))

    def _inferred_type(self, col_index: int) -> DataType:
        name = self.column_names[col_index]
        return self.column_type(name)

    def _convert(self, value: str, dtype: DataType) -> object:
        from splurge_tools.type_helper import String

        defaults = self._type_defaults.get(dtype, {"empty": None, "none": None})
        empty_default = defaults["empty"]
        none_default = defaults["none"]

        if dtype == DataType.MIXED:
            if String.is_none_like(value):
                return none_default
            if String.is_empty_like(value):
                return empty_default
            return value

        if String.is_none_like(value):
            return none_default
        if String.is_empty_like(value):
            return empty_default

        if dtype == DataType.BOOLEAN:
            return String.to_bool(value, default=bool(empty_default))
        if dtype == DataType.INTEGER:
            return String.to_int(value, default=int(empty_default or 0))
        if dtype == DataType.FLOAT:
            return String.to_float(value, default=float(empty_default or 0.0))
        if dtype == DataType.DATE:
            return String.to_date(value, default=empty_default)
        if dtype == DataType.DATETIME:
            return String.to_datetime(value, default=empty_default)
        if dtype == DataType.TIME:
            return String.to_time(value, default=empty_default)
        return value

    def column_type(self, name: str) -> DataType:
        """Infer and cache column type, preferring non-empty/none-like values.

        This mirrors the previous behavior in TypedTabularDataModel to avoid
        over-classifying as MIXED when strong signals exist in non-empty values.
        """
        from splurge_tools.type_helper import profile_values, String
        from splurge_tools.exceptions import SplurgeParameterError

        # Lazy cache on the wrapper to avoid recomputation
        if not hasattr(self, "_typed_column_types"):
            self._typed_column_types: dict[str, DataType] = {}

        if name in self._typed_column_types:
            return self._typed_column_types[name]

        try:
            values: list[str] = self._model.column_values(name)
        except SplurgeParameterError as e:
            raise ValueError(str(e))

        non_empty_values: list[str] = [
            v for v in values if not String.is_empty_like(v) and not String.is_none_like(v)
        ]
        if non_empty_values:
            inferred = profile_values(non_empty_values)
            if inferred != DataType.MIXED:
                self._typed_column_types[name] = inferred
                return inferred

        inferred = profile_values(values)
        self._typed_column_types[name] = inferred
        return inferred
