"""
Streaming tabular data model for large datasets that don't fit in memory.

This class works with streams from DsvHelper.parse_stream to process data
without loading the entire dataset into memory.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import re
from typing import Generator, Iterator

from splurge_tools.protocols import TabularDataProtocol
from splurge_tools.type_helper import DataType, profile_values


class StreamingTabularDataModel(TabularDataProtocol):
    """
    Streaming tabular data model for large datasets that don't fit in memory.
    
    This class works with streams from DsvHelper.parse_stream to process data
    without loading the entire dataset into memory.
    
    This class implements the TabularDataProtocol interface, providing
    a consistent interface for streaming tabular data operations.
    """

    def __init__(
        self,
        stream: Iterator[list[list[str]]],
        *,
        header_rows: int = 1,
        skip_empty_rows: bool = True,
        chunk_size: int = 1000
    ) -> None:
        """
        Initialize StreamingTabularDataModel.

        Args:
            stream (Iterator[list[list[str]]]): Stream of data chunks from DsvHelper.parse_stream.
            header_rows (int): Number of header rows to merge into column names.
            skip_empty_rows (bool): Skip empty rows in data.
            chunk_size (int): Maximum number of rows to keep in memory buffer (minimum 100).

        Raises:
            ValueError: If stream or header configuration is invalid.
        """
        if stream is None:
            raise ValueError("Stream is required")
        if header_rows < 0:
            raise ValueError("Header rows must be greater than or equal to 0")
        if chunk_size < 100:
            raise ValueError("chunk_size must be at least 100")

        self._stream = stream
        self._header_rows = header_rows
        self._skip_empty_rows = skip_empty_rows
        self._chunk_size = chunk_size
        
        # Initialize state
        self._header_data: list[list[str]] = []
        self._column_names: list[str] = []
        self._column_index_map: dict[str, int] = {}
        self._buffer: list[list[str]] = []
        self._max_columns: int = 0
        self._is_initialized: bool = False
        
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
                    # Buffer remaining rows in this chunk (including current), respecting skip_empty_rows
                    if not (self._skip_empty_rows and all(cell.strip() == "" for cell in row)):
                        self._buffer.append(row)
                    
                    # Process remaining rows in the chunk
                    for remaining_row in chunk_iter:
                        if not (self._skip_empty_rows and all(cell.strip() == "" for cell in remaining_row)):
                            self._buffer.append(remaining_row)
                    break
            if header_rows_collected >= self._header_rows:
                break

        # Process headers
        if self._header_rows > 0:
            self._header_data, self._column_names = self.process_headers(
                header_data,
                header_rows=self._header_rows
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
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")
        return self._column_index_map[name]

    @property
    def column_count(self) -> int:
        """
        Number of columns.
        """
        return len(self._column_names)

    def __iter__(self) -> Generator[list[str], None, None]:
        """
        Iterate over all rows in the stream.
        """
        # Yield buffered rows first
        for row in self._buffer:
            # Create a copy of the row to avoid modifying the original
            row_copy = row.copy()
            # Normalize row length
            if len(row_copy) < len(self._column_names):
                row_copy = row_copy + [""] * (len(self._column_names) - len(row_copy))
            elif len(row_copy) > len(self._column_names):
                while len(self._column_names) < len(row_copy):
                    new_col_name = f"column_{len(self._column_names)}"
                    self._column_names.append(new_col_name)
                    self._column_index_map[new_col_name] = len(self._column_names) - 1
            yield row_copy
        self._buffer.clear()
        
        # Then yield remaining rows from stream, chunk by chunk
        for chunk in self._stream:
            for row in chunk:
                if self._skip_empty_rows and all(cell.strip() == "" for cell in row):
                    continue
                # Create a copy of the row to avoid modifying the original
                row_copy = row.copy()
                # Normalize row length
                if len(row_copy) < len(self._column_names):
                    row_copy = row_copy + [""] * (len(self._column_names) - len(row_copy))
                elif len(row_copy) > len(self._column_names):
                    while len(self._column_names) < len(row_copy):
                        new_col_name = f"column_{len(self._column_names)}"
                        self._column_names.append(new_col_name)
                        self._column_index_map[new_col_name] = len(self._column_names) - 1
                yield row_copy

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
        self._is_initialized = False 