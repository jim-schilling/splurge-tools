"""
Factory pattern implementation for splurge-tools package.

This module provides factory classes for creating appropriate data models and components
based on data characteristics and requirements. The factory pattern enables dynamic
selection of the most suitable implementation for a given use case.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import warnings
from typing import Any, Iterator, Optional, Union, Type
from pathlib import Path

from splurge_tools.protocols import (
    TabularDataProtocol,
    DataValidatorProtocol,
    DataTransformerProtocol,
    ResourceManagerProtocol
)
from splurge_tools.tabular_data_model import TabularDataModel
from splurge_tools.typed_tabular_data_model import TypedTabularDataModel
from splurge_tools.streaming_tabular_data_model import StreamingTabularDataModel
from splurge_tools.exceptions import SplurgeValidationError


# Module-level constants for factory configuration
_DEFAULT_MEMORY_THRESHOLD_MB = 100.0  # Default memory threshold for streaming
_DEFAULT_CHUNK_SIZE = 1000  # Default chunk size for streaming models
_MIN_CHUNK_SIZE = 100  # Minimum chunk size for streaming models


class DataModelFactory:
    """
    Factory for creating appropriate data models based on data characteristics.
    
    This factory analyzes data characteristics and creates the most suitable
    data model implementation for the given use case.
    """
    
    def __init__(
        self,
        *,
        memory_threshold_mb: float = _DEFAULT_MEMORY_THRESHOLD_MB,
        default_chunk_size: int = _DEFAULT_CHUNK_SIZE
    ) -> None:
        """
        Initialize DataModelFactory.
        
        Args:
            memory_threshold_mb: Memory threshold in MB for switching to streaming model
            default_chunk_size: Default chunk size for streaming models
        """
        self._memory_threshold_mb = memory_threshold_mb
        self._default_chunk_size = max(default_chunk_size, _MIN_CHUNK_SIZE)
    
    def create_model(
        self,
        data: Union[list[list[str]], Iterator[list[list[str]]]],
        *,
        header_rows: int = 1,
        skip_empty_rows: bool = True,
        force_typed: bool = False,
        force_streaming: bool = False,
        estimated_size_mb: Optional[float] = None,
        type_configs: Optional[dict] = None,
        chunk_size: Optional[int] = None
    ) -> TabularDataProtocol:
        """
        Create the most appropriate data model based on data characteristics.
        
        Args:
            data: Input data as list of lists or iterator
            header_rows: Number of header rows
            skip_empty_rows: Whether to skip empty rows
            force_typed: Force creation of typed model
            force_streaming: Force creation of streaming model
            estimated_size_mb: Estimated data size in MB
            type_configs: Type configurations for typed model
            chunk_size: Chunk size for streaming model
            
        Returns:
            Appropriate data model implementation
            
        Raises:
            SplurgeValidationError: If data is invalid or requirements conflict
        """
        if data is None:
            raise SplurgeValidationError("Data cannot be None")
        
        # Determine the best model type
        model_type = self._determine_model_type(
            data=data,
            force_typed=force_typed,
            force_streaming=force_streaming,
            estimated_size_mb=estimated_size_mb
        )
        
        # Create the appropriate model
        if model_type == "streaming":
            if not isinstance(data, Iterator):
                raise SplurgeValidationError(
                    "Streaming model requires iterator data"
                )
            return self._create_streaming_model(
                data=data,
                header_rows=header_rows,
                skip_empty_rows=skip_empty_rows,
                chunk_size=chunk_size or self._default_chunk_size
            )
        
        elif model_type == "typed":
            if isinstance(data, Iterator):
                raise SplurgeValidationError(
                    "Typed model requires list data, not iterator"
                )
            return self._create_typed_model(
                data=data,
                header_rows=header_rows,
                skip_empty_rows=skip_empty_rows,
                type_configs=type_configs
            )
        
        else:  # standard
            if isinstance(data, Iterator):
                raise SplurgeValidationError(
                    "Standard model requires list data, not iterator"
                )
            return self._create_standard_model(
                data=data,
                header_rows=header_rows,
                skip_empty_rows=skip_empty_rows
            )
    
    def _determine_model_type(
        self,
        data: Union[list[list[str]], Iterator[list[list[str]]]],
        *,
        force_typed: bool,
        force_streaming: bool,
        estimated_size_mb: Optional[float]
    ) -> str:
        """
        Determine the most appropriate model type based on data characteristics.
        
        Args:
            data: Input data
            force_typed: Whether to force typed model
            force_streaming: Whether to force streaming model
            estimated_size_mb: Estimated data size in MB
            
        Returns:
            Model type: "standard", "typed", or "streaming"
        """
        # Check for forced types first
        if force_streaming:
            return "streaming"
        
        if force_typed:
            return "typed"
        
        # Check if data is an iterator (streaming required)
        if isinstance(data, Iterator):
            return "streaming"
        
        # Check estimated size
        if estimated_size_mb is not None and estimated_size_mb > self._memory_threshold_mb:
            return "streaming"
        
        # For list data, prefer typed model for better type safety
        if isinstance(data, list):
            return "typed"
        
        # Default to standard model
        return "standard"
    
    def _create_standard_model(
        self,
        data: list[list[str]],
        *,
        header_rows: int,
        skip_empty_rows: bool
    ) -> TabularDataModel:
        """Create a standard TabularDataModel."""
        return TabularDataModel(
            data=data,
            header_rows=header_rows,
            skip_empty_rows=skip_empty_rows
        )
    
    def _create_typed_model(
        self,
        data: list[list[str]],
        *,
        header_rows: int,
        skip_empty_rows: bool,
        type_configs: Optional[dict]
    ) -> TypedTabularDataModel:
        """Create a TypedTabularDataModel."""
        return TypedTabularDataModel(
            data=data,
            header_rows=header_rows,
            skip_empty_rows=skip_empty_rows,
            type_configs=type_configs
        )
    
    def _create_streaming_model(
        self,
        data: Iterator[list[list[str]]],
        *,
        header_rows: int,
        skip_empty_rows: bool,
        chunk_size: int
    ) -> StreamingTabularDataModel:
        """Create a StreamingTabularDataModel."""
        return StreamingTabularDataModel(
            stream=data,
            header_rows=header_rows,
            skip_empty_rows=skip_empty_rows,
            chunk_size=chunk_size
        )


class ComponentFactory:
    """
    Factory for creating various components used in the splurge-tools package.
    
    This factory provides methods for creating validators, transformers,
    and other components with consistent configuration.
    """
    
    @staticmethod
    def create_validator() -> DataValidatorProtocol:
        """
        Create a data validator instance.
        
        Returns:
            DataValidator instance implementing DataValidatorProtocol
        """
        from splurge_tools.data_validator import DataValidator
        validator = DataValidator()
        
        # Validate that the created object implements the protocol
        if not isinstance(validator, DataValidatorProtocol):
            raise SplurgeValidationError(
                "Created validator does not implement DataValidatorProtocol"
            )
        
        return validator
    
    @staticmethod
    def create_transformer(data_model: TabularDataProtocol) -> DataTransformerProtocol:
        """
        Create a data transformer instance.
        
        Args:
            data_model: The data model to transform
            
        Returns:
            DataTransformer instance implementing DataTransformerProtocol
        """
        from splurge_tools.data_transformer import DataTransformer
        transformer = DataTransformer(data_model)
        
        # Validate that the created object implements the protocol
        if not isinstance(transformer, DataTransformerProtocol):
            raise SplurgeValidationError(
                "Created transformer does not implement DataTransformerProtocol"
            )
        
        return transformer
    
    @staticmethod
    def create_resource_manager(
        file_path: Union[str, Path],
        *,
        mode: str = "r",
        encoding: Optional[str] = None
    ) -> ResourceManagerProtocol:
        """
        Create a file resource manager instance.
        
        Args:
            file_path: Path to the file
            mode: File open mode
            encoding: Text encoding
            
        Returns:
            FileResourceManager instance implementing ResourceManagerProtocol
        """
        from splurge_tools.resource_manager import FileResourceManager
        
        # Create a custom resource manager that wraps FileResourceManager
        class FileResourceManagerWrapper(ResourceManagerProtocol):
            def __init__(self, file_path: Union[str, Path], mode: str, encoding: Optional[str]):
                self._file_manager = FileResourceManager(file_path, mode=mode, encoding=encoding)
                self._file_handle: Optional[Any] = None
                self._is_acquired_flag = False
            
            def acquire(self) -> Any:
                if self._is_acquired_flag:
                    raise SplurgeValidationError("Resource is already acquired")
                
                self._file_handle = self._file_manager.__enter__()
                self._is_acquired_flag = True
                return self._file_handle
            
            def release(self) -> None:
                if not self._is_acquired_flag:
                    return
                
                self._file_manager.__exit__(None, None, None)
                self._file_handle = None
                self._is_acquired_flag = False
            
            def is_acquired(self) -> bool:
                return self._is_acquired_flag
        
        resource_manager = FileResourceManagerWrapper(file_path, mode, encoding)
        
        # Validate that the created object implements the protocol
        if not isinstance(resource_manager, ResourceManagerProtocol):
            raise SplurgeValidationError(
                "Created resource manager does not implement ResourceManagerProtocol"
            )
        
        return resource_manager


# Global factory instance for convenience
_default_factory = DataModelFactory()


def create_data_model(
    data: Union[list[list[str]], Iterator[list[list[str]]]],
    *,
    header_rows: int = 1,
    skip_empty_rows: bool = True,
    force_typed: bool = False,
    force_streaming: bool = False,
    estimated_size_mb: Optional[float] = None,
    type_configs: Optional[dict] = None,
    chunk_size: Optional[int] = None
) -> TabularDataProtocol:
    """
    Convenience function to create a data model using the default factory.
    
    This function provides a simple interface for creating data models without
    explicitly instantiating the factory. It uses the default factory instance
    with standard configuration.
    
    Args:
        data: Input data as list of lists or iterator
        header_rows: Number of header rows
        skip_empty_rows: Whether to skip empty rows
        force_typed: Force creation of typed model
        force_streaming: Force creation of streaming model
        estimated_size_mb: Estimated data size in MB
        type_configs: Type configurations for typed model
        chunk_size: Chunk size for streaming model
        
    Returns:
        Appropriate data model implementation
        
    Raises:
        SplurgeValidationError: If data is invalid or requirements conflict
    """
    return _default_factory.create_model(
        data=data,
        header_rows=header_rows,
        skip_empty_rows=skip_empty_rows,
        force_typed=force_typed,
        force_streaming=force_streaming,
        estimated_size_mb=estimated_size_mb,
        type_configs=type_configs,
        chunk_size=chunk_size
    )
