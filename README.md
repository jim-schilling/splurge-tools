# splurge-tools

A Python package providing comprehensive tools for data type handling, validation, text processing, and streaming data analysis.

## Description

splurge-tools is a collection of Python utilities focused on:
- **Data type handling and validation** with comprehensive type inference and conversion
- **Text file processing and manipulation** with streaming support for large files
- **String tokenization and parsing** with delimited value support
- **Text case transformations** and normalization
- **Delimited separated value (DSV) parsing** with streaming capabilities
- **Tabular data models** for both in-memory and streaming datasets
- **Typed tabular data models** with schema validation
- **Data validation and transformation** utilities
- **Random data generation** for testing and development
- **Memory-efficient streaming** for large datasets that don't fit in RAM
- **Python 3.10+ compatibility** with full type annotations

## Installation

```bash
pip install splurge-tools
```

## Features

### Core Data Processing
- **`type_helper.py`**: Comprehensive type validation, conversion, and inference utilities with support for strings, numbers, dates, times, booleans, and collections
- **`dsv_helper.py`**: Delimited separated value parsing with streaming support, column profiling, and data analysis
- **`tabular_data_model.py`**: In-memory data model for tabular datasets with multi-row header support
- **`typed_tabular_data_model.py`**: Type-safe data model with schema validation and type enforcement
- **`streaming_tabular_data_model.py`**: Memory-efficient streaming data model for large datasets (>100MB)

### Text Processing
- **`text_file_helper.py`**: Text file processing with streaming support, header/footer skipping, and memory-efficient operations
- **`string_tokenizer.py`**: String parsing and tokenization utilities with delimited value support
- **`case_helper.py`**: Text case transformation utilities (camelCase, snake_case, kebab-case, etc.)
- **`text_normalizer.py`**: Text normalization and cleaning utilities

### Data Utilities
- **`data_validator.py`**: Data validation framework with custom validation rules
- **`data_transformer.py`**: Data transformation utilities for converting between formats
- **`random_helper.py`**: Random data generation for testing, including realistic test data and secure Base58-like string generation with guaranteed character diversity
- **`decorators.py`**: Common decorators for handling empty values in string processing methods

### Key Capabilities
- **Streaming Support**: Process datasets larger than available RAM with configurable chunk sizes
- **Type Inference**: Automatic detection of data types including dates, times, numbers, and booleans
- **Multi-row Headers**: Support for complex header structures with automatic merging
- **Memory Efficiency**: Streaming models use minimal memory regardless of dataset size
- **Type Safety**: Full type annotations and validation throughout the codebase
- **Error Handling**: Comprehensive error handling with meaningful error messages
- **Performance**: Optimized for large datasets with efficient algorithms and data structures

## Examples

### Streaming Large Datasets

```python
from splurge_tools.dsv_helper import DsvHelper
from splurge_tools.streaming_tabular_data_model import StreamingTabularDataModel

# Process a large CSV file without loading it into memory
stream = DsvHelper.parse_stream("large_dataset.csv", delimiter=",")
model = StreamingTabularDataModel(stream, header_rows=1, chunk_size=1000)

# Iterate through data efficiently
for row in model:
    # Process each row
    print(row)

# Or get rows as dictionaries
for row_dict in model.iter_rows():
    print(row_dict["column_name"])
```

### Type Inference and Validation

```python
from splurge_tools.type_helper import String, DataType

# Infer data types
data_type = String.infer_type("2023-12-25")  # DataType.DATE
data_type = String.infer_type("123.45")      # DataType.FLOAT
data_type = String.infer_type("true")        # DataType.BOOLEAN

# Convert values with validation
date_val = String.to_date("2023-12-25")
float_val = String.to_float("123.45", default=0.0)
bool_val = String.to_bool("true")
```

### DSV Parsing and Profiling

```python
from splurge_tools.dsv_helper import DsvHelper

# Parse and profile columns
data = DsvHelper.parse("data.csv", delimiter=",")
profile = DsvHelper.profile_columns(data)

# Get column information
for col_name, col_info in profile.items():
    print(f"{col_name}: {col_info['datatype']} ({col_info['count']} values)")
```

### Secure Random String Generation

```python
from splurge_tools.random_helper import RandomHelper

# Generate Base58-like strings with guaranteed character diversity
api_key = RandomHelper.as_base58_like(32)  # Contains alpha, digit, and symbol
print(api_key)  # Example: "A3!bC7@dE9#fG2$hJ4%kL6&mN8*pQ5"

# Generate without symbols (alpha + digits only)
token = RandomHelper.as_base58_like(16, symbols="")
print(token)  # Example: "A3bC7dE9fG2hJ4kL"

# Generate with custom symbols and secure mode
secure_id = RandomHelper.as_base58_like(20, symbols="!@#$", secure=True)
print(secure_id)  # Example: "A3!bC7@dE9#fG2$hJ4"
```

### Empty Value Handling Decorators

The package provides specialized decorators for handling empty values in string processing methods:

```python
from splurge_tools.decorators import (
    handle_empty_value_classmethod,
    handle_empty_value_instancemethod,
    handle_empty_value
)

class StringProcessor:
    @classmethod
    @handle_empty_value_classmethod
    def class_process(cls, value: str) -> str:
        return f"class:{value.upper()}"
    
    @handle_empty_value_instancemethod
    def instance_process(self, value: str) -> str:
        return f"{self.prefix}{value.upper()}"

@handle_empty_value
def standalone_process(value: str) -> str:
    return f"function:{value.upper()}"

# All decorators handle None and empty strings gracefully
StringProcessor.class_process(None)      # Returns ""
StringProcessor.class_process("")        # Returns ""
StringProcessor.class_process("hello")   # Returns "class:HELLO"

# Deprecated method example
@deprecated_method("new_process_method", "2.0.0")
def old_process(value: str) -> str:
    return value.upper()
```

**Decorator Types:**
- **`handle_empty_value_classmethod`**: For `@classmethod` decorated methods
- **`handle_empty_value_instancemethod`**: For instance methods (self as first parameter)
- **`handle_empty_value`**: For standalone methods and `@staticmethod` decorated methods
- **`deprecated_method`**: For marking methods as deprecated with customizable warnings

## Development

### Requirements

- Python 3.10 or higher
- setuptools
- wheel

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jim-schilling/splurge-tools.git
cd splurge-tools
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Testing

Run tests using pytest:
```bash
python -m pytest tests/
```

### Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing with coverage

Run all quality checks:
```bash
black .
isort .
flake8 splurge_tools/ tests/ --max-line-length=120
mypy splurge_tools/
python -m pytest tests/ --cov=splurge_tools
```

### Build

Build distribution:
```bash
python -m build --sdist
```

## Changelog

### [2025.4.3] - 2025-08-25

### [2025.4.2] - 2025-08-22

#### Added
- **Centralized Decorators Module**: Created new `splurge_tools/decorators.py` module to centralize common decorators:
  - **`handle_empty_value_classmethod`**: For `@classmethod` decorated methods that process string values
  - **`handle_empty_value_instancemethod`**: For instance methods (self as first parameter) that process string values
  - **`handle_empty_value`**: For standalone functions and `@staticmethod` decorated methods that process string values
  - **`deprecated_method`**: For marking methods as deprecated with customizable warning messages
- **Enhanced Decorator Examples**: Added comprehensive example demonstrating all decorator types:
  - **`examples/08_decorator_examples.py`**: Complete demonstration of all decorator functionality
  - Shows proper usage patterns for each decorator type
  - Demonstrates empty value handling and deprecation warnings
  - Includes performance metrics and feature coverage validation

#### Changed
- **Decorator Refactoring**: Moved `handle_empty_value` decorator from `case_helper.py` and `text_normalizer.py` to centralized `decorators.py`:
  - Eliminated code duplication across modules
  - Improved maintainability and consistency
  - Enhanced type safety with specialized decorators for different use cases
- **Module Organization**: Moved `deprecated_method` decorator from `common_utils.py` to `decorators.py`:
  - Better separation of concerns (decorators vs utility functions)
  - Improved discoverability of decorator functionality
  - Cleaner module organization
- **Test Organization**: Updated test structure for better maintainability:
  - **`tests/test_decorators.py`**: Comprehensive testing of all decorator functionality
  - Removed duplicate `deprecated_method` tests from `test_common_utils.py`
  - Improved test coverage and organization

#### Fixed
- **Decorator Parameter Handling**: Fixed critical bug in `handle_empty_value` decorator:
  - Corrected parameter signature for class methods (added missing `cls` parameter)
  - Fixed parameter mismatch that caused decorator to fail with valid strings
  - Ensured proper handling of `None` and empty string inputs
- **Test Coverage**: Improved test organization and eliminated duplicate testing:
  - Removed `TestDeprecatedMethod` class from `test_common_utils.py`
  - Centralized all decorator testing in `test_decorators.py`
  - Maintained 100% test coverage for decorators module

#### Performance
- **Test Execution**: Improved test performance with better organization:
  - **527 tests passed** with no failures
  - **95% overall code coverage**
  - **100% coverage** for `decorators.py`
  - **89% coverage** for `common_utils.py`
- **Example Validation**: All examples running successfully:
  - **8/8 examples passed** with comprehensive feature coverage
  - **0.83s total execution time** (0.12s average per example)
  - Validated all major library features working correctly

### [2025.4.1] - 2025-08-16

#### Added
- **Enhanced Base58 Error Handling**: Introduced specific exception types for better error clarity:
  - `Base58Error`: Base class for all base-58 related errors
  - `Base58TypeError`: Raised when input type validation fails
  - `Base58ValidationError`: Raised when base-58 validation fails
- **Improved Base58 Class Structure**: Refactored `Base58` class with better organization:
  - Separated alphabet constants (`DIGITS`, `ALPHA_UPPER`, `ALPHA_LOWER`, `ALPHABET`)
  - Enhanced type checking with specific error messages
  - Improved input validation and error handling

#### Changed
- **Base58 Method Signatures**: Updated method signatures for better type safety:
  - `decode()` method now requires non-None string input
  - `is_valid()` method now requires string input with proper type checking
  - Removed redundant `is_valid_base58()` alias method
- **Enhanced Test Coverage**: Comprehensive test suite improvements:
  - Converted from unittest to pytest for better test organization
  - Added extensive error handling test cases
  - Improved test coverage for edge cases and error conditions
  - Enhanced validation testing for all Base58 operations

#### Fixed
- **Base58 Decoding Edge Cases**: Fixed handling of edge cases in base-58 decoding:
  - Improved handling of all-zero byte sequences
  - Better handling of leading zero bytes in encoded data
  - Enhanced validation for empty and invalid inputs
- **Error Message Clarity**: Improved error messages for better debugging and user experience

#### Performance
- **Test Execution**: Improved test performance and reliability with pytest framework
- **Error Handling**: More efficient error detection and reporting

### [2025.4.0] - 2025-08-13

- Moved to CalVer versioning scheme (Year.Minor.Micro)

#### Breaking Changes
- Removed factory pattern and heuristics:
  - Deleted `DataModelFactory`, `ComponentFactory`, and `create_data_model()`.
  - Introduced explicit constructors in `splurge_tools/factory.py`:
    - `create_in_memory_model(data, *, header_rows=1, skip_empty_rows=True)`
    - `create_streaming_model(stream, *, header_rows=1, skip_empty_rows=True, chunk_size=1000)`
- Removed `TypedTabularDataModel`. Typed access is now provided via a lightweight view:
  - `TabularDataModel.to_typed(type_configs: dict[DataType, Any] | None = None)`
- Simplified protocols and resource management guidance:
  - Streamlined `StreamingTabularDataProtocol` documentation to a minimal, unified interface.
  - Deprecated `ResourceManagerProtocol` usage in favor of direct context managers.

#### Added
- `splurge_tools/tabular_utils.py`: Shared utilities for tabular processing
  - `process_headers()` — multi-row header merging and normalization
  - `normalize_rows()` — row padding and empty-row filtering
  - `should_skip_row()` and `auto_column_names()` helpers
- `TabularDataModel.to_typed()` typed view:
  - Iterates typed rows (`__iter__`, `iter_rows`, `iter_rows_as_tuples`)
  - Random access (`row`, `row_as_list`, `row_as_tuple`)
  - Column APIs (`column_values`, `cell_value`, `column_type`)
  - Lazy conversion with caching; no data duplication

#### Changed
- Unified header and row normalization logic in both in-memory and streaming models using `tabular_utils`.
- Updated examples and tests to use explicit constructors and `to_typed()`; removed factory usage.
- `DataTransformer` import cleanup (removed dependency on deleted `TypedTabularDataModel`).

#### Removed
- `splurge_tools/typed_tabular_data_model.py` and all references.
- Factory helpers and wrapper-based resource manager creation.

#### Fixed
- Typed view default behavior for empty vs. none-like values to match previous semantics:
  - Supports override semantics via `type_configs` (per `DataType`).
  - Distinguishes empty defaults from none defaults for accurate conversions.

#### Migration Guide
- Replace factory usage:
  - `create_data_model(data)` → `create_in_memory_model(data)` or `create_streaming_model(stream)`
  - `ComponentFactory.create_validator()`/`create_transformer()` → instantiate classes directly
- Replace `TypedTabularDataModel(...)` with `TabularDataModel(...).to_typed(...)`.
- Replace `ComponentFactory.create_resource_manager(...)` with `safe_file_operation(...)` or `FileResourceManager` directly.

### [0.3.2] - 2025-08-09

#### Added
- **Secure Float Range Generation**: Enhanced `RandomHelper.as_float_range()` method with new `secure` parameter for cryptographically secure random float generation:
  - Uses Python's `secrets` module when `secure=True` for cryptographically secure randomness
  - Maintains full 64-bit precision for secure random floats using byte-to-float conversion
  - Consistent API with other secure methods in `RandomHelper` class
  - Backward compatible - existing code continues to work unchanged
  - Comprehensive documentation and examples included

- **Comprehensive Examples Suite**: Added complete set of working examples demonstrating all major library features:
  - **`01_type_inference_and_validation.py`**: Type inference, conversion, and validation utilities
  - **`02_dsv_parsing_and_profiling.py`**: DSV parsing, streaming, and column profiling
  - **`03_tabular_data_models.py`**: In-memory, streaming, and typed tabular data models
  - **`04_text_processing.py`**: Text normalization, case conversion, and tokenization
  - **`05_validation_and_transformation.py`**: Data validation, transformation, and factory patterns
  - **`06_random_data_generation.py`**: Random data generation including secure methods
  - **`07_comprehensive_workflows.py`**: End-to-end ETL and streaming data processing workflows
  - **`examples/README.md`**: Comprehensive documentation for all examples
  - **`examples/run_all_examples.py`**: Test runner with performance metrics and feature coverage

#### Changed
- **Example Quality Improvements**: All examples now include:
  - Comprehensive error handling and validation
  - Performance metrics and timing information
  - Windows compatibility (replaced Unicode symbols with ASCII)
  - Detailed explanations and best practices
  - Real-world use cases and practical applications

#### Fixed
- **Method Signature Corrections**: Fixed multiple incorrect method signatures across examples:
  - `DataTransformer.pivot()`: Corrected parameter names (`index_cols`, `columns_col`, `values_col`)
  - `DataTransformer.group_by()`: Fixed aggregation parameter structure (`group_cols`, `agg_dict`)
  - `DataTransformer.transform_column()`: Updated parameter names (`column`, `transform_func`)
  - `TextNormalizer` methods: Corrected method names (`remove_special_chars`, `remove_control_chars`)
  - `Validator` utility methods: Fixed parameter signatures for validation utilities
- **Unicode Compatibility**: Resolved Windows terminal encoding issues by replacing Unicode symbols with ASCII equivalents
- **Import Dependencies**: Fixed missing imports and removed factory pattern references throughout examples
- **Type System Integration**: Replaced `TypedTabularDataModel` with `TabularDataModel.to_typed()` for typed access

#### Performance
- **Example Execution**: All 7 examples now execute successfully with average runtime of 0.12s per example
- **Test Coverage**: 100% success rate across all examples with comprehensive error handling
- **Memory Efficiency**: Examples demonstrate proper streaming techniques for large dataset processing

#### Testing
- **Comprehensive Example Testing**: Added automated test runner that validates all examples execute successfully
- **Feature Coverage Verification**: Test suite verifies all major library features are properly demonstrated
- **Cross-Platform Compatibility**: Examples tested and working on Windows, macOS, and Linux

### [0.3.1] - 2025-08-09

#### Added
- **Common Utilities Module**: Added new `common_utils.py` module containing reusable utility functions to reduce code duplication across the package:
  - `deprecated_method()`: Decorator for marking methods as deprecated with customizable warning messages
  - `safe_file_operation()`: Safe file path validation and operation handling with comprehensive error handling
  - `ensure_minimum_columns()`: Utility for ensuring data rows have minimum required columns with padding
  - `safe_index_access()`: Safe list/tuple index access with bounds checking and helpful error messages
  - `safe_dict_access()`: Safe dictionary key access with default values and error context
  - `validate_data_structure()`: Generic data structure validation with type checking and empty data handling
  - `create_parameter_validator()`: Factory function for creating parameter validation functions from validator dictionaries
  - `batch_validate_rows()`: Iterator for validating and filtering tabular data rows with column count constraints
  - `create_error_context()`: Utility for creating detailed error context information for debugging

- **Validation Utilities Module**: Added new `validation_utils.py` module providing centralized `Validator` class with consistent error handling:
  - `Validator.is_non_empty_string()`: String validation with whitespace handling options
  - `Validator.is_positive_integer()`: Integer validation with range constraints and bounds checking
  - `Validator.is_valid_range()`: Numeric range validation with inclusive/exclusive bounds
  - `Validator.is_valid_path()`: Path validation with existence checking and permission validation
  - `Validator.is_valid_encoding()`: Text encoding validation with fallback options
  - `Validator.is_iterable_of_type()`: Generic iterable validation with element type checking
  - All validator methods follow consistent `is_*` naming convention and return validated values or raise specific exceptions

#### Changed
- **Type Annotation Modernization**: Updated type annotations across multiple modules to use modern Python union syntax (`|`) instead of `Optional` and `Union` imports:
  - Updated `data_transformer.py`, `data_validator.py`, `dsv_helper.py`, `random_helper.py`, `string_tokenizer.py`, `tabular_data_model.py`
  - Improved type safety and consistency throughout the codebase
  - Simplified import statements by removing unused `Optional` and `Union` imports

#### Fixed
- **Enhanced Error Handling**: Improved error handling consistency across the package with specific exception types
- **Code Duplication Reduction**: Consolidated common validation and utility patterns into reusable functions
- **Type Safety Improvements**: Enhanced type checking and validation throughout the codebase

#### Testing
- **Comprehensive Test Coverage**: Added extensive test suites for new modules:
  - `tests/test_common_utils.py`: Complete test coverage for common utility functions (96% coverage)
  - `tests/test_validation_utils.py`: Comprehensive validation utility testing (94% coverage)
  - Enhanced existing test files to use new utility functions where appropriate
- **Maintained Package Coverage**: All existing functionality preserved with improved test organization

### [0.3.0] - 2025-08-08

#### Added
- **Protocol-Based Architecture**: Implemented comprehensive protocol-based design across all major components for improved type safety and consistency
- **StreamingTabularDataProtocol**: Added new `StreamingTabularDataProtocol` specifically designed for streaming data models with methods optimized for memory-efficient processing:
  - `column_names`, `column_count`, `column_index()` for metadata access
  - `__iter__()`, `iter_rows_as_dicts()`, `iter_rows_as_tuples()` for data iteration
  - `reset_stream()` for stream position management
- **DataValidatorProtocol**: Added `DataValidatorProtocol` with required methods `validate()`, `get_errors()`, and `clear_errors()`
- **DataTransformerProtocol**: Added `DataTransformerProtocol` with required methods `transform()` and `can_transform()`
- **TypeInferenceProtocol**: Added `TypeInferenceProtocol` with required methods `can_infer()`, `infer_type()`, and `convert_value()`
- **Enhanced RandomHelper**: Added new `as_base58_like()` method for generating Base58-like strings with guaranteed character diversity:
  - Ensures at least one alphabetic character, one digit, and one symbol (if provided)
  - Validates symbols against the `SYMBOLS` constant for security
  - Supports secure and non-secure random generation modes
  - Includes comprehensive error handling and validation
- **New Constants**: Added `BASE58_ALPHA`, `BASE58_DIGITS`, and `SYMBOLS` constants to `RandomHelper`:
  - `BASE58_ALPHA`: 49 characters (excludes O, I, l from standard alphabet)
  - `BASE58_DIGITS`: 9 characters (excludes 0, uses 1-9 only)
  - `SYMBOLS`: 26 special characters for secure string generation
- **TypeInference Class**: Created new `TypeInference` class implementing `TypeInferenceProtocol` for type inference operations
- **ResourceManager Base Class**: Created new `ResourceManager` base class implementing `ResourceManagerProtocol` with abstract methods `_create_resource()` and `_cleanup_resource()`
- **FileResourceManagerWrapper**: Added adapter class to wrap existing context managers to protocol interface
- **Runtime Protocol Validation**: Added runtime validation in factory methods to ensure created objects implement correct protocols
- **Comprehensive Test Suites**: Added extensive test coverage for all new implementations:
  - `tests/test_factory_protocols.py` - Factory protocol testing
  - `tests/test_type_inference.py` - TypeInference class and protocol testing
  - `tests/test_data_validator_comprehensive.py` - Comprehensive DataValidator testing (98% coverage)
  - `tests/test_factory_comprehensive.py` - Comprehensive Factory testing (87% coverage)
  - `tests/test_resource_manager_comprehensive.py` - Comprehensive ResourceManager testing (84% coverage)
  - Enhanced `test_random_helper.py` with comprehensive `as_base58_like()` testing (97% coverage)

#### Changed
- **StreamingTabularDataModel Protocol Separation**: Updated `StreamingTabularDataModel` to implement `StreamingTabularDataProtocol` instead of `TabularDataProtocol`:
  - Removed methods not suitable for streaming: `row_count`, `column_type`, `column_values`, `cell_value`, `row`, `row_as_list`, `row_as_tuple`
  - Focused on streaming-optimized iteration methods
  - Improved architectural clarity between in-memory and streaming models
- **Factory Return Types**: Enhanced factory methods to correctly return `Union[TabularDataProtocol, StreamingTabularDataProtocol]` based on model type
- **DataValidator Protocol Compliance**: Updated `DataValidator` class to explicitly implement `DataValidatorProtocol`:
  - Modified `validate()` method to return `bool` instead of `Dict[str, List[str]]`
  - Added `get_errors()` method returning list of error messages
  - Added `clear_errors()` method to reset error state
  - Added `_errors` list to track validation errors
  - Kept `validate_detailed()` method for backward compatibility
- **DataTransformer Protocol Compliance**: Updated `DataTransformer` class to explicitly implement `DataTransformerProtocol`:
  - Added `transform()` method providing general transformation capability
  - Added `can_transform()` method to check transformability
  - Updated constructor to accept `TabularDataProtocol` for broader compatibility
  - Kept existing specific transformation methods (pivot, melt, group_by, etc.)
- **Factory Pattern Improvements**: Enhanced `ComponentFactory` methods to return proper protocol types instead of `Any`:
  - Added runtime validation for protocol compliance
  - Updated type hints throughout factory classes
  - Added proper error handling for protocol compliance failures
- **Test Organization**: Updated existing test suites to include protocol compliance testing and improved test structure

#### Fixed
- **Type Annotation Issues**: Resolved 109 MyPy type errors across the codebase:
  - Fixed decorator type signatures in `case_helper.py` and `text_normalizer.py`
  - Corrected unreachable code issues in `type_helper.py` by restructuring type checks
  - Fixed `None` attribute access by adding proper `isinstance()` checks
  - Updated generic type parameters throughout (`Iterator[Any]`, `list[Any]`, `dict[str, DataType]`)
  - Corrected `PathLike` type annotations to `PathLike[str]`
  - Fixed resource manager type annotations for file handles and temporary files
- **Protocol Implementation Issues**: Resolved all protocol compliance issues across the codebase
- **Type Safety**: Fixed factory methods to return proper protocol types with runtime validation
- **Circular Import Issues**: Resolved circular import problems in type inference components
- **Parameter Type Issues**: Fixed parameter types to handle `None` values properly:
  - Updated `string_tokenizer.py`, `base58.py` parameter types to `str | None` or `Any`
  - Added proper validation in `random_helper.py` for `start` parameter
- **Test Failures**: Fixed 7 test failures related to protocol type assertions in factory tests
- **Backward Compatibility**: Ensured all existing functionality remains intact while adding protocol compliance

#### Performance
- **Test Coverage Improvements**: Significant improvements in test coverage across core components:
  - DataValidator: 67% → **100%** (+33%)
  - Factory: 85% → **89%** (+4%)
  - ResourceManager: 42% → **84%** (+42%)
  - TypeHelper: 51% → **71%** (+20%)
  - RandomHelper: 58% → **97%** (+39%)
- **Type Safety**: Reduced MyPy errors from 109 to 7 (remaining are "unreachable code" warnings for defensive programming)
- **Architectural Clarity**: Improved separation of concerns between streaming and in-memory data models

### [0.2.7] - 2025-08-01

#### Added
- Added `utility_helper.py` module with base-58 encoding/decoding utilities
- Added `encode_base58()` function for converting binary data to base-58 strings
- Added `decode_base58()` function for converting base-58 strings to binary data
- Added `is_valid_base58()` function for validating base-58 string format
- Added `ValidationError` exception class for utility validation errors
- Added comprehensive test suite for base-58 functionality in `test_utility_helper.py`
- Added support for bytearray input in base-58 encoding
- Added handling for edge cases including all-zero bytes and leading zeros
- Added integration tests for cryptographic key encoding and Bitcoin-style addresses
- Added performance and memory efficiency tests for large data handling
- Added concurrent operation testing for thread safety

#### Changed
- Enhanced error handling with specific validation error messages
- Improved input validation for base-58 encoding/decoding operations

#### Fixed
- Proper handling of leading zero bytes in base-58 encoding/decoding
- Correct validation of base-58 alphabet characters (excluding 0, O, I, l)

### [0.2.6] - 2025-07-12

#### Added
- **Incremental Type Checking Optimization**: Added performance optimization to `profile_values()` function in `type_helper.py` that uses weighted incremental checks at 25%, 50%, and 75% of data processing to short-circuit early when a definitive type can be determined. This provides significant performance improvements for large datasets (>10,000 items) while maintaining accuracy.
- **Early Mixed Type Detection**: Enhanced early termination logic to immediately return `MIXED` type when both numeric/temporal types and string types are detected, avoiding unnecessary processing.
- **Configurable Optimization**: Added `use_incremental_typecheck` parameter (default: `True`) to control whether incremental checking is used, allowing users to disable optimization if needed.
- **Performance Benchmarking**: Added comprehensive performance benchmark script (`examples/profile_values_performance_benchmark.py`) demonstrating 2-3x performance improvements for large datasets.

#### Changed
- **Performance Threshold**: Incremental type checking is automatically disabled for datasets of 10,000 items or fewer to avoid overhead on small datasets.
- **Documentation Updates**: Updated docstrings in `type_helper.py` to accurately reflect the simplified implementation.
- **Test Structure**: Updated unittest test classes to properly inherit from `unittest.TestCase` for improved test organization and consistency.

#### Removed
- **Unused Imports**: Removed unused `os` import from `type_helper.py` to improve code cleanliness.


### [0.2.5] - 2025-07-10

#### Changed
- **Test Organization**: Reorganized test files to improve clarity and maintainability by separating core functionality tests from complex/integration tests. Split the following test files:
  - `test_dsv_helper.py`: Kept core parsing tests; moved file I/O and streaming tests to `test_dsv_helper_file_stream.py`
  - `test_streaming_tabular_data_model.py`: Kept core streaming model tests; moved complex scenarios and edge cases to `test_streaming_tabular_data_model_complex.py`
  - `test_text_file_helper.py`: Kept core text file operations; moved streaming tests to `test_text_file_helper_streaming.py`
- **Import Cleanup**: Removed unused import statements from all test files to improve code quality and maintainability:
  - Removed unused `DataType` import from `test_dsv_helper.py`
  - Removed unused `Iterator` imports from streaming tabular data model test files
- **String Class Refactoring**: Migrated method-level constants to class-level constants in `type_helper.py` String class for improved performance and maintainability:
  - Moved date/time/datetime pattern lists to class-level constants (`_DATE_PATTERNS`, `_TIME_PATTERNS`, `_DATETIME_PATTERNS`)
  - Moved regex patterns to class-level constants (`_FLOAT_REGEX`, `_INTEGER_REGEX`, `_DATE_YYYY_MM_DD_REGEX`, etc.)
  - This eliminates repeated pattern compilation on each method call and improves code organization

#### Fixed
- **Test Expectations**: Fixed test failures related to incorrect expectations for `profile_columns` method keys (`datatype` instead of `type` and no `count` key) and adjusted error message regex in streaming tabular data model tests.
- **String Class Regex Patterns**: Fixed regex patterns in `type_helper.py` String class for datetime parsing. Updated `_DATETIME_YYYY_MM_DD_REGEX` and `_DATETIME_MM_DD_YYYY_REGEX` patterns to properly handle microseconds with `[.]?\d+` instead of the incorrect `[.]?\d{5}` pattern.

#### Testing
- **Maintained Coverage**: All 167 tests continue to pass with 96% code coverage after reorganization and cleanup.
- **Improved Maintainability**: Test organization now provides clearer separation between core functionality and complex scenarios, enabling selective test execution and better code organization.

### [0.2.4] - 2025-07-05

#### Fixed
- **profile_values Edge Case**: Fixed edge case in `profile_values` function where collections of all-digit strings that could be interpreted as different types (DATE, TIME, DATETIME, INTEGER) were being classified as MIXED instead of INTEGER. The function now prioritizes INTEGER type when all values are all-digit strings (with optional +/- signs) and there's a mix of DATE, TIME, DATETIME, and INTEGER interpretations.
- **profile_values Iterator Safety**: Fixed issue where `profile_values` function would fail when given a non-reusable iterator (e.g., generator). The function now uses a 2-pass approach that always uses a list for the special case logic is needed, ensuring both correctness with generators.

### [0.2.3] - 2025-07-05

#### Changed
- **API Simplification**: Removed the `multi_row_headers` parameter from `TabularDataModel`, `StreamingTabularDataModel`, and `DsvHelper.profile_columns`. Multi-row header merging is now controlled solely by the `header_rows` parameter.
- **StreamingTabularDataModel API Refinement**: Streamlined the `StreamingTabularDataModel` API to focus on streaming functionality by removing random access methods (`row()`, `row_as_list()`, `row_as_tuple()`, `cell_value()`) and column analysis methods (`column_values()`, `column_type()`). This creates a cleaner, more consistent streaming paradigm.
- **Tests and Examples Updated**: All tests and example scripts have been updated to use only the `header_rows` parameter for multi-row header merging. Any usage of `multi_row_headers` has been removed.
- **StringTokenizer Tests Refactored**: Consolidated and removed redundant tests in `test_string_tokenizer.py` for improved maintainability and clarity. Test coverage and edge case handling remain comprehensive.

#### Added
- **StreamingTabularDataModel**: New streaming tabular data model for large datasets that don't fit in memory. Works with streams from `DsvHelper.parse_stream` to process data without loading the entire dataset into memory. Features include:
  - Memory-efficient streaming processing with configurable chunk sizes (minimum 100 rows)
  - Support for multi-row headers with automatic merging
  - Multiple iteration methods (as lists, dictionaries, tuples)
  - Empty row skipping and uneven row handling
  - Comprehensive error handling and validation
  - Dynamic column expansion during iteration
  - Row padding for uneven data
- **Comprehensive Test Coverage**: Added extensive test suite for `StreamingTabularDataModel` with 26 test methods covering:
  - Basic functionality with and without headers
  - Multi-row header processing
  - Buffer operations and memory management
  - Iteration methods (direct, dict, tuple)
  - Error handling for invalid parameters and columns
  - Edge cases (empty files, large datasets, uneven rows, empty headers)
  - Header validation and initialization
  - Chunk processing and buffer size limits
  - Dynamic column expansion and row padding
- **Streaming Data Example**: Added comprehensive example demonstrating `StreamingTabularDataModel` usage, including memory usage comparison with traditional loading methods.

#### Fixed
- **Header Processing**: Fixed header processing logic in all data models (`StreamingTabularDataModel`, `TabularDataModel`) to properly handle empty headers by filling them with `column_<index>` names. Headers like `"Name,,City"` now correctly become `["Name", "column_1", "City"]`.
- **DSV Parsing**: Fixed `StringTokenizer.parse` to preserve empty fields instead of filtering them out. This ensures that `"Name,,City"` is parsed as `["Name", "", "City"]` instead of `["Name", "City"]`, maintaining data integrity.
- **Row Padding and Dynamic Column Expansion**: Fixed row padding logic in `StreamingTabularDataModel` to properly handle uneven rows and dynamically expand columns during iteration.
- **File Handling**: Fixed file permission errors in tests by ensuring proper cleanup of temporary files and stream exhaustion.

#### Performance
- **Memory Efficiency**: `StreamingTabularDataModel` provides significant memory savings for large datasets by processing data in configurable chunks rather than loading entire files into memory.
- **Streaming Processing**: Enables processing of datasets larger than available RAM through efficient streaming and buffer management.

#### Testing
- **94% Test Coverage**: Achieved 94% test coverage for `StreamingTabularDataModel` with comprehensive edge case testing.
- **Error Condition Testing**: Added thorough testing of error conditions including invalid parameters and missing columns.
- **Integration Testing**: Tests cover integration with `DsvHelper.parse_stream` and various data formats.
- **StringTokenizer Tests Updated**: Updated `StringTokenizer` tests to reflect the new behavior of preserving empty fields.

### [0.2.2] - 2025-07-04

#### Added
- **TextFileHelper.load_as_stream**: Added new method for memory-efficient streaming of large text files with configurable chunk sizes. Supports header/footer row skipping and uses optimized deque-based sliding window for footer handling.
- **TextFileHelper.preview skip_header_rows parameter**: Added `skip_header_rows` parameter to the `preview()` method, allowing users to skip header rows when previewing file contents.

#### Performance
- **TextFileHelper Footer Buffer Optimization**: Replaced list-based footer buffer with `collections.deque` in `load_as_stream()` method, improving performance from O(n) to O(1) for footer row operations.

#### Fixed
- **TabularDataModel No-Header Scenarios**: Fixed issue where column names were empty when `header_rows=0`. Column names are now properly generated as `["column_0", "column_1", "column_2"]` when no headers are provided.
- **TabularDataModel Row Access**: Fixed `IndexError` in the `row()` method when accessing uneven data rows. Added proper padding logic to ensure row data has enough columns before access.
- **TabularDataModel Data Normalization**: Improved consistency between column count and column names by ensuring column names always match the actual column count, regardless of header configuration.

### [0.2.1] - 2025-07-03

#### Added
- **DsvHelper.profile_columns**: Added `DsvHelper.profile_columns`, a new method that generates a simple data profile from parsed DSV data, inferring column names and datatypes.
- **Test Coverage**: Added comprehensive test cases for `DsvHelper.profile_columns` and improved validation of DSV parsing logic, including edge cases for all supported datatypes.

### [0.2.0] - 2025-07-02

#### Breaking Changes
- **Method Signature Standardization**: All method signatures across the codebase have been updated to require default parameters to be named (e.g., `def myfunc(value: str, *, trim: bool = True)`). This enforces keyword-only arguments for all default values, improving clarity and consistency. This is a breaking change and may require updates to any code that calls these methods positionally for defaulted parameters.
- All method signatures now use explicit type annotations and follow PEP8 and project-specific conventions for parameter ordering and naming.
- Some methods may have reordered parameters or stricter type requirements as part of this standardization.

### Fixed
- **Resolved Regex Pattern Bug**: Fixed regex pattern bug - ?? should have been ? in String class in type_helper.py.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Development

### Building Source Distributions

This project is configured to build source distributions only (no wheels). To build a source distribution:

```bash
# Using the build script (recommended)
python build_sdist.py

# Or using build directly
python -m build --sdist
```

The source distribution will be created in the `dist/` directory as a `.tar.gz` file.

### Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=splurge_tools --cov-report=html
```

## Author

Jim Schilling
