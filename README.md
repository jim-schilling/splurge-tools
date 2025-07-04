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

### [0.2.2] - 2025-07-04

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
