"""
Streaming tabular data model for large datasets that don't fit in memory.

This class works with streams from DsvHelper.parse_stream to process data
without loading the entire dataset into memory.

Copyright (c) 2025, Jim Schilling

This module is licensed under the MIT License.
"""

import re
from typing import Generator, Iterator

from splurge_tools.type_helper import DataType, profile_values


class StreamingTabularDataModel:
    """
    Streaming tabular data model for large datasets that don't fit in memory.
    
    This class works with streams from DsvHelper.parse_stream to process data
    without loading the entire dataset into memory.
    """

    def __init__(
        self,
        stream: Iterator[list[list[str]]],
        *,
        header_rows: int = 1,
        multi_row_headers: int = 1,
        skip_empty_rows: bool = True,
        chunk_size: int = 1000
    ) -> None:
        """
        Initialize StreamingTabularDataModel.

        Args:
            stream (Iterator[list[list[str]]]): Stream of data chunks from DsvHelper.parse_stream.
            header_rows (int): Number of header rows.
            multi_row_headers (int): Number of rows to merge for column names.
            skip_empty_rows (bool): Skip empty rows in data.
            chunk_size (int): Maximum number of rows to keep in memory buffer (minimum 100).

        Raises:
            ValueError: If stream or header configuration is invalid.
        """
        if stream is None:
            raise ValueError("Stream is required")
        if header_rows < 0:
            raise ValueError("Header rows must be greater than or equal to 0")
        if header_rows > 0 and multi_row_headers > header_rows:
            raise ValueError("Column names span must be less than or equal to header rows")
        if header_rows > 0 and multi_row_headers == 0:
            raise ValueError("Column names span must be greater than 0 if header rows are greater than 0")
        if chunk_size < 100:
            raise ValueError("chunk_size must be at least 100")

        self._stream = stream
        self._header_rows = header_rows
        self._multi_row_headers = multi_row_headers
        self._skip_empty_rows = skip_empty_rows
        self._chunk_size = chunk_size
        
        # Initialize state
        self._header_data: list[list[str]] = []
        self._column_names: list[str] = []
        self._column_index_map: dict[str, int] = {}
        self._column_types: dict[str, DataType] = {}
        self._buffer: list[list[str]] = []
        self._total_rows_processed: int = 0
        self._max_columns: int = 0
        self._is_initialized: bool = False
        self._row_count: int = 0  # Track total rows yielded
        
        # Process headers and initialize
        self._initialize_from_stream()

    def _initialize_from_stream(self) -> None:
        """
        Initialize the model by processing headers from the stream.
        """
        if self._is_initialized:
            return

        # Collect header rows from the stream
        header_rows_collected = 0
        header_data: list[list[str]] = []
        
        for chunk in self._stream:
            chunk_iter = iter(chunk)
            for row in chunk_iter:
                if header_rows_collected < self._header_rows:
                    header_data.append(row)
                    header_rows_collected += 1
                else:
                    # Buffer all remaining rows in this chunk (including current)
                    self._buffer.append(row)
                    self._buffer.extend(list(chunk_iter))
                    break
            if header_rows_collected >= self._header_rows:
                break

        # Process headers
        if self._header_rows > 0:
            self._header_data, self._column_names = self.process_headers(
                header_data,
                header_rows=self._header_rows,
                multi_row_headers=self._multi_row_headers
            )
        else:
            # No headers, generate column names from first data row
            if self._buffer:
                self._max_columns = len(self._buffer[0])
                self._column_names = [f"column_{i}" for i in range(self._max_columns)]

        # Create column index map
        self._column_index_map = {name: i for i, name in enumerate(self._column_names)}
        self._is_initialized = True

    @staticmethod
    def process_headers(
        header_data: list[list[str]],
        *,
        header_rows: int,
        multi_row_headers: int
    ) -> tuple[list[list[str]], list[str]]:
        """
        Process header data to create merged headers and column names.

        Args:
            header_data (list[list[str]]): Raw header data rows.
            header_rows (int): Number of header rows.
            multi_row_headers (int): Number of rows to merge for column names.

        Returns:
            tuple[list[list[str]], list[str]]: Processed header data and column names.
        """
        processed_header_data = header_data.copy()
        
        # Merge multi-row headers if needed
        if header_rows > 1 and multi_row_headers > 1:
            merged_headers: list[str] = []
            for i in range(min(multi_row_headers, len(header_data))):
                row = header_data[i]
                while len(merged_headers) < len(row):
                    merged_headers.append("")
                for j, name in enumerate(row):
                    if merged_headers[j]:
                        merged_headers[j] = f"{merged_headers[j]}_{name}"
                    else:
                        merged_headers[j] = name
            processed_header_data = [merged_headers]

        # Extract and normalize column names
        column_names = processed_header_data[0] if len(processed_header_data) > 0 else []
        column_names = [re.sub(r"\s+", " ", name).strip() for name in column_names]

        # Determine column count from header data
        column_count = 0
        if header_data:
            column_count = max(len(row) for row in header_data)

        # Handle empty column names and ensure proper column count
        if len(column_names) == 0:
            column_names = [f"column_{i}" for i in range(column_count)]

        while len(column_names) < column_count:
            column_names.append(f"column_{len(column_names)}")

        # Handle empty individual column names
        column_names = [name if name else f"column_{i}" for i, name in enumerate(column_names)]

        return processed_header_data, column_names

    def _fill_buffer(self) -> None:
        """
        Fill the buffer with up to chunk_size rows from the stream (for random access methods).
        """
        while len(self._buffer) < self._chunk_size:
            try:
                chunk = next(self._stream)
            except StopIteration:
                break
            for row in chunk:
                if self._skip_empty_rows and all(cell.strip() == "" for cell in row):
                    continue
                if len(row) < len(self._column_names):
                    row = row + [""] * (len(self._column_names) - len(row))
                elif len(row) > len(self._column_names):
                    while len(self._column_names) < len(row):
                        new_col_name = f"column_{len(self._column_names)}"
                        self._column_names.append(new_col_name)
                        self._column_index_map[new_col_name] = len(self._column_names) - 1
                self._buffer.append(row)
                if len(self._buffer) >= self._chunk_size:
                    break

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
        Number of rows yielded so far (for streaming, this is updated during iteration).
        """
        return self._row_count

    @property
    def column_count(self) -> int:
        """
        Number of columns.
        """
        return len(self._column_names)

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
            # Sample values from buffer for type inference
            self._fill_buffer()
            values: list[str] = [row[col_idx] for row in self._buffer if col_idx < len(row)]
            self._column_types[name] = profile_values(values)
        return self._column_types[name]

    def column_values(
        self,
        name: str
    ) -> list[str]:
        """
        Get all values for a column from the buffer.

        Args:
            name (str): Column name.

        Returns:
            list[str]: Values in the column from current buffer.

        Raises:
            ValueError: If column name is not found.
        """
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")
        col_idx: int = self._column_index_map[name]
        self._fill_buffer()
        return [row[col_idx] for row in self._buffer if col_idx < len(row)]

    def cell_value(
        self,
        name: str,
        row_index: int
    ) -> str:
        """
        Get a cell value by column name and row index from buffer.

        Args:
            name (str): Column name.
            row_index (int): Row index (0-based, relative to buffer).

        Returns:
            str: Cell value.

        Raises:
            ValueError: If column name is not found or row index is out of range.
        """
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")
        col_idx: int = self._column_index_map[name]
        self._fill_buffer()
        if row_index < 0 or row_index >= len(self._buffer):
            raise ValueError(f"Row index {row_index} out of range")
        return self._buffer[row_index][col_idx]

    def __iter__(self) -> Generator[list[str], None, None]:
        """
        Iterate over all rows in the stream.
        """
        # Yield buffered rows first
        for row in self._buffer:
            self._row_count += 1
            yield row
        self._buffer.clear()
        # Then yield remaining rows from stream, chunk by chunk
        for chunk in self._stream:
            for row in chunk:
                if self._skip_empty_rows and all(cell.strip() == "" for cell in row):
                    continue
                # Normalize row length
                if len(row) < len(self._column_names):
                    row = row + [""] * (len(self._column_names) - len(row))
                elif len(row) > len(self._column_names):
                    while len(self._column_names) < len(row):
                        new_col_name = f"column_{len(self._column_names)}"
                        self._column_names.append(new_col_name)
                        self._column_index_map[new_col_name] = len(self._column_names) - 1
                self._row_count += 1
                yield row

    def iter_rows(self) -> Generator[dict[str, str], None, None]:
        """
        Iterate over rows as dictionaries.
        """
        for row in self:
            yield dict(zip(self._column_names, row))

    def iter_rows_as_tuples(self) -> Generator[tuple[str, ...], None, None]:
        """
        Iterate over rows as tuples.
        """
        for row in self:
            yield tuple(row)

    def row(
        self,
        index: int
    ) -> dict[str, str]:
        """
        Get a row as a dictionary from buffer.

        Args:
            index (int): Row index (0-based, relative to buffer).

        Returns:
            dict[str, str]: Row as a dictionary.

        Raises:
            ValueError: If row index is out of range.
        """
        self._fill_buffer()
        if index < 0 or index >= len(self._buffer):
            raise ValueError(f"Row index {index} out of range")
        
        row_data = self._buffer[index]
        # Ensure row_data is properly padded to match column count
        padded_row = row_data + [""] * (len(self._column_names) - len(row_data))
        return {
            self._column_names[i]: padded_row[i]
            for i in range(len(self._column_names))
        }

    def row_as_list(
        self,
        index: int
    ) -> list[str]:
        """
        Get a row as a list from buffer.

        Args:
            index (int): Row index (0-based, relative to buffer).

        Returns:
            list[str]: Row as a list.

        Raises:
            ValueError: If row index is out of range.
        """
        self._fill_buffer()
        if index < 0 or index >= len(self._buffer):
            raise ValueError(f"Row index {index} out of range")
        return self._buffer[index]

    def row_as_tuple(
        self,
        index: int
    ) -> tuple[str, ...]:
        """
        Get a row as a tuple from buffer.

        Args:
            index (int): Row index (0-based, relative to buffer).

        Returns:
            tuple[str, ...]: Row as a tuple.

        Raises:
            ValueError: If row index is out of range.
        """
        return tuple(self.row_as_list(index))

    def clear_buffer(self) -> None:
        """
        Clear the current buffer to free memory.
        """
        self._buffer.clear()

    def reset_stream(self) -> None:
        """
        Reset the stream position (requires a new stream iterator).
        """
        self._buffer.clear()
        self._total_rows_processed = 0
        self._is_initialized = False 