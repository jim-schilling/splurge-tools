"""
This module contains the TypedTabularDataModel class that extends TabularDataModel
to provide typed data access.

Copyright (c) 2025, Jim Schilling

Please keep the copyright notice in this file and in the source code files.

This module is licensed under the MIT License.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Generator, Optional, Union

from splurge_tools.tabular_data_model import TabularDataModel
from splurge_tools.type_helper import DataType, String, profile_values


@dataclass
class TypeConfig:
    """
    Configuration for how to handle empty and none-like values for a specific data type.

    Attributes:
        empty_default: Default value to use for empty-like values
        none_default: Default value to use for none-like values
    """

    empty_default: Any
    none_default: Any


class TypedTabularDataModel(TabularDataModel):
    """
    A class that extends TabularDataModel to provide typed data access.
    Values are automatically converted to their native Python types based on
    the inferred column type.
    """

    def __init__(
        self,
        data: list[list[str]],
        header_rows: int = 1,
        multi_row_headers: int = 1,
        skip_empty_rows: bool = True,
        type_configs: Optional[dict[DataType, TypeConfig]] = None,
    ):
        super().__init__(data, header_rows, multi_row_headers, skip_empty_rows)
        self._typed_data: list[list[Any]] = []

        # Set up default type configurations
        self._type_configs = {
            DataType.BOOLEAN: TypeConfig(False, False),
            DataType.INTEGER: TypeConfig(0, 0),
            DataType.FLOAT: TypeConfig(0.0, 0.0),
            DataType.DATE: TypeConfig(None, None),
            DataType.DATETIME: TypeConfig(None, None),
            DataType.STRING: TypeConfig("", ""),
            DataType.MIXED: TypeConfig("", None),  # For mixed types, treat as string
            DataType.EMPTY: TypeConfig("", ""),
            DataType.NONE: TypeConfig(None, None),
            DataType.TIME: TypeConfig(None, None),
        }

        # Override with user-provided configurations
        if type_configs:
            self._type_configs.update(type_configs)

        self._convert_data()

    def _convert_data(self) -> None:
        """Convert all data to their native Python types based on column types."""
        # First infer all column types
        for col_name in self._column_names:
            self.column_type(col_name)

        # Then convert all values
        self._typed_data = []
        for row in self._data:
            typed_row = []
            for i, value in enumerate(row):
                col_name = self._column_names[i]
                col_type = self._column_types[col_name]
                typed_row.append(self._convert_value(value, col_type))
            self._typed_data.append(typed_row)

    def _convert_value(self, value: str, data_type: DataType) -> Any:
        """
        Convert a string value to its native Python type based on the DataType.

        Args:
            value: The string value to convert
            data_type: The DataType to convert to

        Returns:
            The converted value in its native Python type
        """
        type_config = self._type_configs[data_type]

        # For MIXED type, handle empty/none values differently
        if data_type == DataType.MIXED:
            if String.is_none_like(value):
                return type_config.none_default
            return value  # Preserve empty values as-is

        # Handle empty and none-like values based on the data type's configuration
        if String.is_empty_like(value):
            return type_config.empty_default
        if String.is_none_like(value):
            return type_config.none_default

        # Convert based on data type
        if data_type == DataType.BOOLEAN:
            return String.to_bool(value, default=type_config.empty_default)
        elif data_type == DataType.INTEGER:
            return String.to_int(value, default=type_config.empty_default)
        elif data_type == DataType.FLOAT:
            return String.to_float(value, default=type_config.empty_default)
        elif data_type == DataType.DATE:
            return String.to_date(value, default=type_config.empty_default)
        elif data_type == DataType.DATETIME:
            return String.to_datetime(value, default=type_config.empty_default)
        elif data_type == DataType.TIME:
            return String.to_time(value, default=type_config.empty_default)
        else:
            return value

    def column_values(self, name: str) -> list[Any]:
        """
        Get all values for a column in their native Python type.

        Args:
            name: Column name to get values for

        Returns:
            List of values in the column in their native Python type

        Raises:
            ValueError: If column name is not found
        """
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")

        col_idx = self._column_index_map[name]
        return [row[col_idx] for row in self._typed_data]

    def cell_value(self, name: str, row_index: int) -> Any:
        """
        Get a cell value by column name and row index in its native Python type.

        Args:
            name: Column name
            row_index: Row index (0-based)

        Returns:
            Cell value in its native Python type

        Raises:
            ValueError: If column name is not found or row index is out of range
        """
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")
        if row_index < 0 or row_index >= self._rows:
            raise ValueError(f"Row index {row_index} out of range")

        col_idx = self._column_index_map[name]
        return self._typed_data[row_index][col_idx]

    def iter_rows(self) -> Generator[dict[str, Any], None, None]:
        """
        Iterate over rows as dictionaries with native Python types.
        This is more efficient than calling row() for each index.
        """
        for row in self._typed_data:
            yield dict(zip(self._column_names, row))

    def iter_rows_as_tuples(self) -> Generator[tuple[Any, ...], None, None]:
        """
        Iterate over rows as tuples with native Python types.
        This is more efficient than calling row_as_tuple() for each index.
        """
        for row in self._typed_data:
            yield tuple(row)

    def row(self, index: int) -> dict[str, Any]:
        """
        Get a row as a dictionary with native Python types.

        Args:
            index: Row index (0-based)

        Returns:
            Dictionary mapping column names to values

        Raises:
            ValueError: If row index is out of range
        """
        if index < 0 or index >= self._rows:
            raise ValueError(f"Row index {index} out of range")

        return {
            self._column_names[i]: self._typed_data[index][i]
            for i in range(self._columns)
        }

    def row_as_list(self, index: int) -> list[Any]:
        """
        Get a row as a list with native Python types.

        Args:
            index: Row index (0-based)

        Returns:
            List of values in the row

        Raises:
            ValueError: If row index is out of range
        """
        if index < 0 or index >= self._rows:
            raise ValueError(f"Row index {index} out of range")
        return self._typed_data[index]

    def row_as_tuple(self, index: int) -> tuple[Any, ...]:
        """
        Get a row as a tuple with native Python types.

        Args:
            index: Row index (0-based)

        Returns:
            Tuple of values in the row

        Raises:
            ValueError: If row index is out of range
        """
        if index < 0 or index >= self._rows:
            raise ValueError(f"Row index {index} out of range")
        return tuple(self._typed_data[index])

    def column_type(self, name: str) -> DataType:
        """
        Get the inferred data type for a column.
        This is cached for the column.

        Args:
            name: Column name to get type for

        Returns:
            DataType enum value representing the inferred type

        Raises:
            ValueError: If column name is not found
        """
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")

        if name not in self._column_types:
            col_idx = self._column_index_map[name]
            values = [row[col_idx] for row in self._data]

            # First try to infer the type without empty/none values
            non_empty_values = [
                v
                for v in values
                if not String.is_empty_like(v) and not String.is_none_like(v)
            ]
            if non_empty_values:
                inferred_type = profile_values(non_empty_values)
                if inferred_type != DataType.MIXED:
                    self._column_types[name] = inferred_type
                    return inferred_type

            # If we couldn't infer a type from non-empty values, try all values
            self._column_types[name] = profile_values(values)

        return self._column_types[name]
