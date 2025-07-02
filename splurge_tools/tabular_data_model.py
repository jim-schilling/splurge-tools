"""
Tabular data model classes for structured data operations.

Copyright (c) 2025, Jim Schilling

This module is licensed under the MIT License.
"""

import re
from typing import Generator

from splurge_tools.type_helper import DataType, profile_values


class TabularDataModel:
    """
    Tabular data model for structured data.
    """

    def __init__(
        self,
        data: list[list[str]],
        *,
        header_rows: int = 1,
        multi_row_headers: int = 1,
        skip_empty_rows: bool = True
    ) -> None:
        """
        Initialize TabularDataModel.

        Args:
            data (list[list[str]]): Raw data rows.
            header_rows (int): Number of header rows.
            multi_row_headers (int): Number of rows to merge for column names.
            skip_empty_rows (bool): Skip empty rows in data.

        Raises:
            ValueError: If data or header configuration is invalid.
        """
        if data is None or len(data) == 0:
            raise ValueError("Data is required")
        if header_rows < 0:
            raise ValueError("Header rows must be greater than or equal to 0")
        if header_rows > 0 and multi_row_headers > header_rows:
            raise ValueError("Column names span must be less than or equal to header rows")
        if header_rows > 0 and multi_row_headers == 0:
            raise ValueError("Column names span must be greater than 0 if header rows are greater than 0")

        self._raw_data = data
        self._header_rows = header_rows
        self._multi_row_headers = multi_row_headers
        self._header_data = data[:header_rows] if header_rows > 0 else []
        self._data = (
            self._normalize_data_model(data[header_rows:], skip_empty_rows)
            if header_rows > 0
            else self._normalize_data_model(data, skip_empty_rows)
        )
        self._header_columns = len(self._header_data[0]) if len(self._header_data) > 0 else 0
        self._columns = len(self._data[0]) if len(self._data) > 0 else 0
        self._rows = len(self._data) if len(self._data) > 0 else 0

        if header_rows > 1 and multi_row_headers > 1:
            merged_headers: list[str] = []
            for i in range(min(multi_row_headers, len(self._header_data))):
                row = self._header_data[i]
                while len(merged_headers) < len(row):
                    merged_headers.append("")
                for j, name in enumerate(row):
                    if merged_headers[j]:
                        merged_headers[j] = f"{merged_headers[j]}_{name}"
                    else:
                        merged_headers[j] = name
            self._header_data = [merged_headers]

        self._column_names = self._header_data[0] if len(self._header_data) > 0 else []
        self._column_names = [re.sub(r"\s+", " ", name).strip() for name in self._column_names]

        if len(self._column_names) == 0:
            self._column_names = [f"column_{i}" for i in range(self._columns)]

        while len(self._column_names) < self._columns:
            self._column_names.append(f"column_{len(self._column_names)}")

        self._column_names = [name if name else f"column_{i}" for i, name in enumerate(self._column_names)]
        self._column_index_map = {name: i for i, name in enumerate(self._column_names)}
        self._column_types = {}

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
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")
        return self._column_index_map[name]

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
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")
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
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")
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
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")
        if row_index < 0 or row_index >= self._rows:
            raise ValueError(f"Row index {row_index} out of range")
        col_idx: int = self._column_index_map[name]
        return self._data[row_index][col_idx]

    def __iter__(self) -> Generator[list[str], None, None]:
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
        return {
            self._column_names[i]: self._data[index][i] for i in range(self._columns)
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
        if len(rows) == 0:
            return []
        max_column_count: int = max(len(row) for row in rows)
        normalized_rows: list[list[str]] = []
        for row in rows:
            if len(row) < max_column_count:
                row = row + [""] * (max_column_count - len(row))
            normalized_rows.append(row)
        if skip_empty_rows:
            normalized_rows = [
                row
                for row in normalized_rows
                if not all(cell.strip() == "" for cell in row)
            ]
        return normalized_rows
