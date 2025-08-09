"""
This module contains the TypedTabularDataModel class that extends TabularDataModel
for typed data access.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

from dataclasses import dataclass
from typing import Any, Generator, Optional

from splurge_tools.protocols import TabularDataProtocol
from splurge_tools.tabular_data_model import TabularDataModel
from splurge_tools.type_helper import DataType, String, profile_values


@dataclass
class TypeConfig:
    """
    Configuration for handling empty and none-like values for a specific data type.
    """
    empty_default: Any
    none_default: Any


class TypedTabularDataModel(TabularDataModel, TabularDataProtocol):
    """
    Extends TabularDataModel to provide typed data access.
    Values are converted to native Python types based on inferred column type.
    
    This class implements the TabularDataProtocol interface, providing
    a consistent interface for typed tabular data operations.
    """

    def __init__(
        self,
        data: list[list[str]],
        *,
        header_rows: int = 1,
        skip_empty_rows: bool = True,
        type_configs: Optional[dict[DataType, TypeConfig]] = None
    ) -> None:
        super().__init__(
            data,
            header_rows=header_rows,
            skip_empty_rows=skip_empty_rows
        )
        self._typed_data: list[list[Any]] = []
        self._type_configs = {
            DataType.BOOLEAN: TypeConfig(False, False),
            DataType.INTEGER: TypeConfig(0, 0),
            DataType.FLOAT: TypeConfig(0.0, 0.0),
            DataType.DATE: TypeConfig(None, None),
            DataType.DATETIME: TypeConfig(None, None),
            DataType.STRING: TypeConfig("", ""),
            DataType.MIXED: TypeConfig("", None),
            DataType.EMPTY: TypeConfig("", ""),
            DataType.NONE: TypeConfig(None, None),
            DataType.TIME: TypeConfig(None, None),
        }
        if type_configs:
            self._type_configs.update(type_configs)
        self._convert_data()

    def _convert_data(self) -> None:
        """
        Convert all data to native Python types based on column types.
        """
        for col_name in self._column_names:
            self.column_type(col_name)
        self._typed_data = [
            [self._convert_value(value, self._column_types[self._column_names[i]]) for i, value in enumerate(row)]
            for row in self._data
        ]

    def _convert_value(
        self,
        value: str,
        data_type: DataType
    ) -> Any:
        """
        Convert a string value to its native Python type based on the DataType.
        """
        type_config: TypeConfig = self._type_configs[data_type]
        if data_type == DataType.MIXED:
            if String.is_none_like(value):
                return type_config.none_default
            return value
        if String.is_empty_like(value):
            return type_config.empty_default
        if String.is_none_like(value):
            return type_config.none_default
        if data_type == DataType.BOOLEAN:
            return String.to_bool(value, default=type_config.empty_default)
        if data_type == DataType.INTEGER:
            return String.to_int(value, default=type_config.empty_default)
        if data_type == DataType.FLOAT:
            return String.to_float(value, default=type_config.empty_default)
        if data_type == DataType.DATE:
            return String.to_date(value, default=type_config.empty_default)
        if data_type == DataType.DATETIME:
            return String.to_datetime(value, default=type_config.empty_default)
        if data_type == DataType.TIME:
            return String.to_time(value, default=type_config.empty_default)
        return value

    def column_values(
        self,
        name: str
    ) -> list[Any]:
        """
        Get all values for a column in their native Python type.
        """
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")
        col_idx: int = self._column_index_map[name]
        return [row[col_idx] for row in self._typed_data]

    def cell_value(
        self,
        name: str,
        row_index: int
    ) -> Any:
        """
        Get a cell value by column name and row index in its native Python type.
        """
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")
        if row_index < 0 or row_index >= self._rows:
            raise ValueError(f"Row index {row_index} out of range")
        col_idx: int = self._column_index_map[name]
        return self._typed_data[row_index][col_idx]

    def iter_rows(self) -> Generator[dict[str, Any], None, None]:
        """
        Iterate over rows as dictionaries with native Python types.
        """
        for row in self._typed_data:
            yield dict(zip(self._column_names, row))

    def iter_rows_as_tuples(self) -> Generator[tuple[Any, ...], None, None]:
        """
        Iterate over rows as tuples with native Python types.
        """
        for row in self._typed_data:
            yield tuple(row)

    def row(
        self,
        index: int
    ) -> dict[str, Any]:
        """
        Get a row as a dictionary with native Python types.
        """
        if index < 0 or index >= self._rows:
            raise ValueError(f"Row index {index} out of range")
        return {
            self._column_names[i]: self._typed_data[index][i]
            for i in range(self._columns)
        }

    def row_as_list(
        self,
        index: int
    ) -> list[Any]:
        """
        Get a row as a list with native Python types.
        """
        if index < 0 or index >= self._rows:
            raise ValueError(f"Row index {index} out of range")
        return self._typed_data[index]

    def row_as_tuple(
        self,
        index: int
    ) -> tuple[Any, ...]:
        """
        Get a row as a tuple with native Python types.
        """
        if index < 0 or index >= self._rows:
            raise ValueError(f"Row index {index} out of range")
        return tuple(self._typed_data[index])

    def column_type(
        self,
        name: str
    ) -> DataType:
        """
        Get the inferred data type for a column. Cached for the column.
        """
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")
        if name not in self._column_types:
            col_idx: int = self._column_index_map[name]
            values: list[str] = [row[col_idx] for row in self._data]
            non_empty_values: list[str] = [
                v for v in values if not String.is_empty_like(v) and not String.is_none_like(v)
            ]
            if non_empty_values:
                inferred_type: DataType = profile_values(non_empty_values)
                if inferred_type != DataType.MIXED:
                    self._column_types[name] = inferred_type
                    return inferred_type
            self._column_types[name] = profile_values(values)
        return self._column_types[name]
