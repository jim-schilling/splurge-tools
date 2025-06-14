"""
This module contains the classes for the tabular data model.

Copyright (c) 2025, Jim Schilling

Please keep the copyright notice in this file and in the source code files.

This module is licensed under the MIT License.
"""
import re
from typing import Generator

class TabularDataModel:
    """
    This class represents a tabular data model.
    """
    def __init__(
            self, 
            data: list[list[str]],
            header_rows: int = 1,
            multi_row_headers: int = 1,
            skip_empty_rows: bool = True
    ):
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
        self._data = self._normalize_data_model(data[header_rows:], skip_empty_rows) if header_rows > 0 else self._normalize_data_model(data, skip_empty_rows)
        self._header_columns = len(self._header_data[0]) if len(self._header_data) > 0 else 0
        self._columns = len(self._data[0]) if len(self._data) > 0 else 0
        self._rows = len(self._data) if len(self._data) > 0 else 0
        
        # if header_rows > 1 and multi_row_headers > 1, then merge the header data into a single row
        if header_rows > 1 and multi_row_headers > 1:
            # For multi-row headers, combine the first multi_row_headers rows
            merged_headers = []
            for i in range(min(multi_row_headers, len(self._header_data))):
                row = self._header_data[i]
                # Extend column names if needed
                while len(merged_headers) < len(row):
                    merged_headers.append('')
                # Combine with existing names
                for j, name in enumerate(row):
                    if merged_headers[j]:
                        merged_headers[j] = f"{merged_headers[j]}_{name}"
                    else:
                        merged_headers[j] = name
            self._header_data = [merged_headers]
        
        # Get column names from the first row of header data
        self._column_names = self._header_data[0] if len(self._header_data) > 0 else []
        
        # strip away 2 or more spaces from the column names
        self._column_names = [re.sub(r'\s+', ' ', name).strip() for name in self._column_names]
        
        # If no headers, generate column names
        if len(self._column_names) == 0:
            self._column_names = [f"column_{i}" for i in range(self._columns)]
        
        # ensure column_names matches the number of columns and replace empty names
        while len(self._column_names) < self._columns:
            self._column_names.append(f"column_{len(self._column_names)}")
        
        # Replace any empty column names with column_n
        self._column_names = [name if name else f"column_{i}" for i, name in enumerate(self._column_names)]
            
        self._column_index_map = {name: i for i, name in enumerate(self._column_names)}
        
    @property
    def column_names(self) -> list[str]:
        """
        The column names.
        """
        return self._column_names  
       
    def column_index(self, name: str) -> int:
        """
        Get the column index for a given name.
        If the column name is not found, raise a ValueError.
        """
        if name not in self._column_index_map:
            raise ValueError(f"Column name {name} not found")
        return self._column_index_map[name]
    
    @property
    def row_count(self) -> int:
        """
        The number of rows.
        """
        return self._rows
    
    @property
    def column_count(self) -> int:
        """
        The number of columns.
        """
        return self._columns
    
    # setup an iterator for the data
    def __iter__(self):
        return iter(self._data)
    
    def iter_rows(self) -> Generator[dict[str, str], None, None]:
        """
        Iterate over rows as dictionaries.
        This is more efficient than calling row() for each index.
        """
        for row in self._data:
            yield dict(zip(self._column_names, row))
    
    def iter_rows_as_tuples(self) -> Generator[tuple[str, ...], None, None]:
        """
        Iterate over rows as tuples.
        This is more efficient than calling row_as_tuple() for each index.
        """
        for row in self._data:
            yield tuple(row)
    
    # return a row as a dictionary
    def row(self, index: int) -> dict[str, str]:
        """
        Get a row as a dictionary.
        """
        return {self._column_names[i]: self._data[index][i] for i in range(self._columns)}
    
    # return a row as a list
    def row_as_list(self, index: int) -> list[str]:
        """
        Get a row as a list.
        """
        return self._data[index]
    
    # return a row as a tuple
    def row_as_tuple(self, index: int) -> tuple[str, ...]:
        """
        Get a row as a tuple.
        """
        return tuple(self._data[index])
    
    @staticmethod
    def _normalize_data_model(rows: list[list[str]], skip_empty_rows: bool = True) -> list[list[str]]:
        """
        Normalize the data model.
        """
        # if the rows are empty, return an empty list
        if len(rows) == 0:
            return []
        
        # ensure that the rows are all the same length, fill in the missing values with empty strings
        max_column_count = max(len(row) for row in rows)
        normalized_rows = []
        for row in rows:
            if len(row) < max_column_count:
                row = row + [''] * (max_column_count - len(row))
            normalized_rows.append(row)
        
        if skip_empty_rows:
            normalized_rows = [row for row in normalized_rows if not all(cell.strip() == '' for cell in row)]
        
        return normalized_rows