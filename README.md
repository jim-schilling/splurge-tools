# splurge-tools

A Python package providing tools for data type handling, validation, and text processing.

## Description

splurge-tools is a collection of Python utilities focused on:
- Data type handling and validation
- Text file processing and manipulation
- String tokenization and parsing
- Text case transformations
- Delimited separated value parsing
- Tabular data model class
- Typed tabular data model class
- Data validator class
- Random data class
- Data transformation class
- Text normalizer class
- Python 3.10+ compatibility

## Installation

```bash
pip install splurge-tools
```

## Features

- `type_helper.py`: Comprehensive type validation and conversion utilities
- `text_file_helper.py`: Text file processing and manipulation tools
- `string_tokenizer.py`: String parsing and tokenization utilities
- `case_helper.py`: Text case transformation utilities
- `dsv_helper.py`: Delimited separated value utilities
- `tabular_data_model.py`: Data model for tabular datasets
- `typed_tabular_data_model.py`: Type data model based on tabular data model
- `data_validator.py`: Data validator class
- `random_helper.py`: Random data class and methods for generating data
- `data_transformer.py`: Data transformation utility class
- `text_normalizer.py`: Text normalization utility class

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
python -m build
```

## Changelog

# [0.2.5] - 2025-07-10

### [0.2.4] - 2025-07-05

#### Fixed
- **profile_values Edge Case**: Fixed edge case in `profile_values` function where collections of all-digit strings that could be interpreted as different types (DATE, TIME, DATETIME, INTEGER) were being classified as MIXED instead of INTEGER. The function now prioritizes INTEGER type when all values are all-digit strings (with optional +/- signs) and there's a mix of DATE, TIME, DATETIME, and INTEGER interpretations.
- **profile_values Iterator Safety**: Fixed issue where `profile_values` function would fail when given a non-reusable iterator (e.g., generator). The function now uses a 2-pass approach that always uses a list for the special case logic is needed, ensuring both correctness with generators.

### [0.2.3] - 2025-07-05

#### Changed
- **API Simplification**: Removed the `multi_row_headers` parameter from `TabularDataModel`, `StreamingTabularDataModel`, `TypedTabularDataModel`, and `DsvHelper.profile_columns`. Multi-row header merging is now controlled solely by the `header_rows` parameter, which specifies how many rows to merge for column names. This change simplifies the API and eliminates redundant parameters.
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
- **Header Processing**: Fixed header processing logic in all data models (`StreamingTabularDataModel`, `TabularDataModel`, `TypedTabularDataModel`) to properly handle empty headers by filling them with `column_<index>` names. Headers like `"Name,,City"` now correctly become `["Name", "column_1", "City"]`.
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

## Author

Jim Schilling
