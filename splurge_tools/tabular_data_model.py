"""
Tabular data model classes for structured data operations.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import re
import warnings
from typing import Generator, Iterator

from splurge_tools.protocols import TabularDataProtocol
from splurge_tools.type_helper import DataType, profile_values
from splurge_tools.validation_utils import Validator
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

        # Process headers using the new public method
        self._header_data, self._column_names = self.process_headers(
            self._header_data,
            header_rows=header_rows
        )
        
        # Ensure column names match the actual column count
        while len(self._column_names) < self._columns:
            self._column_names.append(f"column_{len(self._column_names)}")
        self._column_index_map = {name: i for i, name in enumerate(self._column_names)}
        self._column_types: dict[str, DataType] = {}

    @staticmethod
    def process_headers(
        header_data: list[list[str]],
        *,
        header_rows: int
    ) -> tuple[list[list[str]], list[str]]:
        """
        Process header data to create merged headers and column names.

        Args:
            header_data (list[list[str]]): Raw header data rows.
            header_rows (int): Number of header rows to merge.

        Returns:
            tuple[list[list[str]], list[str]]: Processed header data and column names.
        """
        processed_header_data = header_data.copy()
        
        # Merge multi-row headers if needed
        if header_rows > 1:
            merged_headers: list[str] = []
            for i in range(len(header_data)):
                row = header_data[i]
                while len(merged_headers) < len(row):
                    merged_headers.append("")
                for j, name in enumerate(row):
                    if merged_headers[j]:
                        merged_headers[j] = f"{merged_headers[j]}_{name}"
                    else:
                        merged_headers[j] = name
            processed_header_data = [merged_headers]

        # Extract and normalize column names, always fill empty with column_<index>
        if processed_header_data and processed_header_data[0]:
            raw_names = processed_header_data[0]
            column_names = [
                re.sub(r"\s+", " ", name).strip() if name and re.sub(r"\s+", " ", name).strip() else f"column_{i}"
                for i, name in enumerate(raw_names)
            ]
        else:
            column_names = []

        # Ensure column_names matches the max column count
        column_count = max(len(row) for row in header_data) if header_data else 0
        while len(column_names) < column_count:
            column_names.append(f"column_{len(column_names)}")

        return processed_header_data, column_names

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
