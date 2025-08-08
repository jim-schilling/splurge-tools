"""
Protocol definitions for splurge-tools package.

This module defines Protocol classes that establish contracts for common interfaces
used throughout the package. These protocols enable better type checking and
ensure consistent behavior across related classes.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

from typing import Any, Iterator, Generator, Protocol, runtime_checkable
from collections.abc import Iterable

from splurge_tools.type_helper import DataType


@runtime_checkable
class TabularDataProtocol(Protocol):
    """
    Protocol for tabular data models.
    
    This protocol defines the interface that all tabular data models should implement,
    ensuring consistent behavior across different implementations.
    """
    
    @property
    def column_names(self) -> list[str]:
        """Get the list of column names."""
        ...
    
    @property
    def row_count(self) -> int:
        """Get the number of data rows."""
        ...
    
    @property
    def column_count(self) -> int:
        """Get the number of columns."""
        ...
    
    def column_index(self, name: str) -> int:
        """Get the index of a column by name."""
        ...
    
    def column_type(self, name: str) -> DataType:
        """Get the inferred data type of a column."""
        ...
    
    def column_values(self, name: str) -> list[str]:
        """Get all values for a specific column."""
        ...
    
    def cell_value(self, name: str, row_index: int) -> str:
        """Get the value of a specific cell."""
        ...
    
    def row(self, index: int) -> dict[str, str]:
        """Get a row as a dictionary."""
        ...
    
    def row_as_list(self, index: int) -> list[str]:
        """Get a row as a list."""
        ...
    
    def row_as_tuple(self, index: int) -> tuple[str, ...]:
        """Get a row as a tuple."""
        ...
    
    def __iter__(self) -> Iterator[list[str]]:
        """Iterate over rows as lists."""
        ...
    
    def iter_rows(self) -> Generator[dict[str, str], None, None]:
        """Iterate over rows as dictionaries."""
        ...
    
    def iter_rows_as_tuples(self) -> Generator[tuple[str, ...], None, None]:
        """Iterate over rows as tuples."""
        ...


@runtime_checkable
class DataValidatorProtocol(Protocol):
    """
    Protocol for data validation.
    
    This protocol defines the interface for data validation components,
    ensuring consistent validation behavior across different implementations.
    """
    
    def validate(self, data: Any) -> bool:
        """Validate the given data."""
        ...
    
    def get_errors(self) -> list[str]:
        """Get list of validation errors."""
        ...
    
    def clear_errors(self) -> None:
        """Clear all validation errors."""
        ...


@runtime_checkable
class DataTransformerProtocol(Protocol):
    """
    Protocol for data transformation operations.
    
    This protocol defines the interface for data transformation components,
    ensuring consistent transformation behavior across different implementations.
    """
    
    def transform(self, data: TabularDataProtocol) -> TabularDataProtocol:
        """Transform the given data."""
        ...
    
    def can_transform(self, data: TabularDataProtocol) -> bool:
        """Check if the data can be transformed."""
        ...


@runtime_checkable
class TypeInferenceProtocol(Protocol):
    """
    Protocol for type inference operations.
    
    This protocol defines the interface for type inference components,
    ensuring consistent type inference behavior across different implementations.
    """
    
    def can_infer(self, value: str) -> bool:
        """Check if the value can be inferred as a specific type."""
        ...
    
    def infer_type(self, value: str) -> DataType:
        """Infer the type of the given value."""
        ...
    
    def convert_value(self, value: str) -> Any:
        """Convert the value to its inferred type."""
        ...


@runtime_checkable
class ResourceManagerProtocol(Protocol):
    """
    Protocol for resource management operations.
    
    This protocol defines the interface for resource management components,
    ensuring consistent resource handling behavior across different implementations.
    """
    
    def acquire(self) -> Any:
        """Acquire the managed resource."""
        ...
    
    def release(self) -> None:
        """Release the managed resource."""
        ...
    
    def is_acquired(self) -> bool:
        """Check if the resource is currently acquired."""
        ...
