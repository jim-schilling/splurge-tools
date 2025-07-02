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

### [0.2.0] - 2025-07-02

#### Breaking Changes
- **Method Signature Standardization**: All method signatures across the codebase have been updated to require default parameters to be named (e.g., `def myfunc(value: str, *, trim: bool = True)`). This enforces keyword-only arguments for all default values, improving clarity and consistency. This is a breaking change and may require updates to any code that calls these methods positionally for defaulted parameters.
- All method signatures now use explicit type annotations and follow PEP8 and project-specific conventions for parameter ordering and naming.
- Some methods may have reordered parameters or stricter type requirements as part of this standardization.

#### Added
- Enhanced time type handling with comprehensive test coverage
- Added support for 12-hour time format with microseconds (e.g., "2:30:45.123456 PM")
- Added boundary condition tests for time parsing (midnight, noon, end of day)
- Added edge case testing for invalid time formats and invalid boundary conditions
- Added comprehensive time type inference tests

#### Fixed
- Fixed parsing bug for 4-digit time format "1430" (was incorrectly parsed as 14:03, now correctly parsed as 14:30)
- Reordered time parsing patterns to prioritize more specific formats before general ones
- Added missing pattern "%I:%M:%S.%f %p" for 12-hour time with microseconds and AM/PM

#### Changed
- Improved time type detection and conversion robustness
- Enhanced test coverage for time-related functionality to 96% overall coverage

### [0.1.13] - 2025-06-30

#### Added
- Added `String.is_time_like()` and `String.to_time()` for time value detection and conversion in `type_helper.py`
- `DataType.TIME` is now fully supported in type inference and profiling
- Added tests for time detection, conversion, and inference
- Enhanced `pyproject.toml` configuration following Python best practices
- Added comprehensive development dependencies (pytest, black, isort, flake8, mypy, pre-commit)
- Added project URLs for better discoverability
- Added keywords and improved classifiers for PyPI
- Added `py.typed` marker for type checking support
- Added tool configurations for Black, isort, mypy, pytest, and coverage
- Added optional dependency groups (dev, test, build)

#### Changed
- Updated development workflow to use modern Python packaging standards
- Improved test configuration with coverage reporting
- Enhanced code formatting and import organization

#### Fixed
- Code formatting issues across all modules
- Import sorting and organization

### [0.1.12] - 2025-06-30
- Rename to splurge-tools

### [0.1.11] - 2025-06-29

#### Added
- Added `String.is_time_like()` and `String.to_time()` for time value detection and conversion in `type_helper.py`
- `DataType.TIME` is now fully supported in type inference and profiling
- Added tests for time detection, conversion, and inference
- Enhanced `pyproject.toml` configuration following Python best practices
- Added comprehensive development dependencies (pytest, black, isort, flake8, mypy, pre-commit)
- Added project URLs for better discoverability
- Added keywords and improved classifiers for PyPI
- Added `py.typed` marker for type checking support
- Added tool configurations for Black, isort, mypy, pytest, and coverage
- Added optional dependency groups (dev, test, build)

#### Changed
- Updated development workflow to use modern Python packaging standards
- Improved test configuration with coverage reporting
- Enhanced code formatting and import organization

#### Fixed
- Code formatting issues across all modules
- Import sorting and organization

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Jim Schilling
